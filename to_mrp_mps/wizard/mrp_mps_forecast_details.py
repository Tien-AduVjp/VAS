from odoo import api, fields, models


class MpsForecastDetails(models.TransientModel):
    _name = 'mrp.mps.forecast.details'
    _description = 'Forecast Demand Details'

    move_ids = fields.Many2many('stock.move', string='Stock Moves', readonly=True)
    purchase_order_line_ids = fields.Many2many('purchase.order.line', string='Purchase Order Details', readonly=True)
    rfq_qty = fields.Integer('Qty from RFQ', compute='_compute_quantity')
    moves_qty = fields.Integer('Qty from Incoming Moves', compute='_compute_quantity')
    manufacture_qty = fields.Integer('Qty from Manufacturing Order', compute='_compute_quantity')
    total_qty = fields.Integer('Actual Replenishment', compute='_compute_quantity')

    @api.depends('move_ids', 'purchase_order_line_ids')
    def _compute_quantity(self):
        for r in self:
            r.moves_qty = sum(r.move_ids.filtered(lambda m: m.picking_id).mapped('product_qty'))
            r.manufacture_qty = sum(r.move_ids.filtered(lambda m: m.production_id).mapped('product_qty'))
            r.rfq_qty = sum(r.purchase_order_line_ids.mapped(lambda l: l.product_uom._compute_quantity(l.product_qty, l.product_id.uom_id)))
            r.total_qty = r.moves_qty + r.manufacture_qty + r.rfq_qty

    def action_view_incoming_moves(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.env.context.get('action_name'),
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('id', 'in', self.move_ids.picking_id.ids)],
            'target': 'current',
        }

    def action_view_rfqs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.env.context.get('action_name'),
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('id', 'in', self.purchase_order_line_ids.order_id.ids)],
            'target': 'current',
        }

    def action_view_mo(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.env.context.get('action_name'),
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('id', 'in', self.move_ids.production_id.ids)],
            'target': 'current',
        }
