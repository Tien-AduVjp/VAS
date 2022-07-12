from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockBarcodeLot(models.TransientModel):
    _name = "stock_barcode.lot"
    _inherit = ['barcodes.barcode_events_mixin']
    _description = "SN/LN Scanning Wizard"

    picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    product_id = fields.Many2one('product.product', string='Product')
    default_move_id = fields.Many2one('stock.move', string='Default Stock Move')
    qty_reserved = fields.Float('Reserved Qty')
    qty_done = fields.Float('Done Qty')
    stock_barcode_lot_line_ids = fields.One2many('stock_barcode.lot.line', 'stock_barcode_lot_id')

    @api.model
    def default_get(self, fields_list):
        res = super(StockBarcodeLot, self).default_get(fields_list)
        qty_reserved = 0.0
        qty_done = 0.0
        candidate_ids = self.env.context.get('candidates', False)
        if 'stock_barcode_lot_line_ids' in fields_list and candidate_ids:
            candidates = self.env['stock.move.line'].browse(candidate_ids)
            lines = []
            res['default_move_id'] = candidates[0].move_id.id
            for ml in candidates:
                lot_name = ml.lot_id and ml.lot_id.name or ml.lot_name
                lines.append({
                    'lot_name': lot_name,
                    'qty_reserved': ml.product_uom_qty,
                    'qty_done': ml.qty_done,
                    'move_line_id': ml.id,
                })
                qty_reserved += ml.product_uom_qty
                qty_done += ml.qty_done
            res['stock_barcode_lot_line_ids'] = [(0, 0, l) for l in lines]
        if 'qty_reserved' in fields_list:
            res['qty_reserved'] = qty_reserved
        if 'qty_done' in fields_list:
            res['qty_done'] = qty_done

        return res

    def on_barcode_scanned(self, barcode):
        line = self.stock_barcode_lot_line_ids.filtered(lambda l: l.lot_name == barcode or not l.lot_name)[:1]
        vals = {}
        if line:
            if line.lot_name and self.product_id.tracking == 'serial' and line.qty_done > 0:
                raise UserError(_('You cannot scan one serial number twice'))
            line.lot_name = barcode
            line.qty_done += 1
        else:
            vals['lot_name'] = barcode
            vals['qty_done'] = 1
            vals['stock_barcode_lot_id'] = self.id
            self.env['stock_barcode.lot.line'].new(vals)
        return

    def _get_or_create_lot(self, barcode):
        lot = self.env['stock.production.lot'].search([
            ('name', '=', barcode),
            ('product_id', '=', self.product_id.id)
        ], limit=1)
        if not lot:
            lot = self.env['stock.production.lot'].create({
                'name': barcode,
                'product_id': self.product_id.id
            })
        return lot

    def _prepare_new_stock_move_vals(self, move_line_vals):
        self.ensure_one()
        return {
            'name': self.picking_id.name,
            'picking_id': self.picking_id.id,
            'picking_type_id': self.picking_id.picking_type_id.id,
            'location_id': self.picking_id.location_id.id,
            'location_dest_id': self.picking_id.location_dest_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'move_line_ids': [(0, 0, move_line_vals)]
        }

    def action_validate(self):
        for line in self.stock_barcode_lot_line_ids:
            if line.lot_name:
                move_line_vals = {}
                move_line_vals['qty_done'] = line.qty_done

                if self.picking_id.picking_type_id.use_create_lots and not self.picking_id.picking_type_id.use_existing_lots:
                    move_line_vals['lot_name'] = line.lot_name
                else:
                    move_line_vals['lot_id'] = self._get_or_create_lot(line.lot_name).id

                if line.move_line_id:
                    line.move_line_id.write(move_line_vals)
                elif self.default_move_id:
                    move_line_vals.update({
                        'picking_id': self.picking_id.id,
                        'move_id': self.default_move_id.id,
                        'product_id': self.product_id.id,
                        'product_uom_id': self.default_move_id.product_uom.id,
                        'location_id': self.default_move_id.location_id.id,
                        'location_dest_id': self.default_move_id.location_dest_id.id,
                    })
                    self.env['stock.move.line'].create(move_line_vals)
                else:
                    move_line_vals.update({
                        'picking_id': self.picking_id.id,
                        'product_id': self.product_id.id,
                        'product_uom_id': self.product_id.uom_id.id,
                        'location_id': self.picking_id.location_id.id,
                        'location_dest_id': self.picking_id.location_dest_id.id,
                    })
                    new_move = self.env['stock.move'].create(self._prepare_new_stock_move_vals(move_line_vals))
                    self.default_move_id = new_move


class StockBarcodeLotLine(models.TransientModel):
    _name = "stock_barcode.lot.line"
    _description = "SN/LN Scanning Wizard Line"

    stock_barcode_lot_id = fields.Many2one('stock_barcode.lot')
    lot_name = fields.Char('Lot')
    qty_reserved = fields.Float('Reserved Qty')
    qty_done = fields.Float('Done Qty')
    move_line_id = fields.Many2one('stock.move.line', string='Product Move')
