from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    production_lot_id = fields.Many2one('stock.production.lot', string='Lot/Seria Number', readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one(compute='_compute_product_id', readonly=True, states={'draft': [('readonly', False)]}, store=True)
    stock_move_line_ids = fields.One2many('stock.move.line', 'account_asset_asset_id', string='Stock Move Lines', readonly=True)
    stock_input_account_id = fields.Many2one('account.account', string='Stock Input Account',
                                                       domain=[('deprecated', '=', False)],
                                                       readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]},
                                                       help="Accounts are used in the stock re-input action, "
                                                       "to support different entries generation method upon asset.\n"
                                                       "When no account is set here, the Stock Input Account "
                                                       "on Asset Category will be used instead.")
    
    def _get_locations(self):
        self.ensure_one()
        picking = self.stock_move_line_ids.mapped('picking_id')
        if picking:
            return picking.location_id.id, picking.location_dest_id.id
        else:
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'asset_allocation'),
                ('warehouse_id.company_id', '=', self.env.company.id),
            ], limit=1)
            return picking_type.default_location_src_id.id, picking_type.default_location_dest_id.id
    
    @api.constrains('state', 'production_lot_id')
    def _check_state(self):
        lot_ids = self.search([('id', 'not in', self.ids), ('state', '=', 'open')]).mapped('production_lot_id').ids
        if lot_ids:
            assets = self.filtered(lambda asset: asset.state == 'open' and asset.production_lot_id.id in lot_ids)
            if assets:
                raise UserError(_('Lot/Seria Number \"%s\" for asset exists.') % assets[0].production_lot_id.name)

    @api.constrains('date_first_depreciation', 'first_depreciation_date', 'date')
    def _check_first_depreciation_date(self):
        super(AccountAssetAsset, self)._check_first_depreciation_date()

        move_lines = self.env['stock.move.line'].search([('state', '=', 'done'), ('lot_id', 'in', self.production_lot_id.ids)]) \
                    .filtered(lambda line: line.location_dest_id.usage == 'internal')
        move_lines.read(['account_asset_asset_id', 'date'])
        for r in self:
            dates = move_lines.filtered(lambda line: line.account_asset_asset_id.id != r.id).mapped('date')
            if dates:
                date = max(dates).date()
                first_depreciation_date = r.date_first_depreciation == 'manual' and r.first_depreciation_date or r.date
                if date > first_depreciation_date:
                    raise UserError(_('The first depreciation date cannot be set before purchase date/stock input date!'))
    
    @api.depends('production_lot_id')
    def _compute_product_id(self):
        for r in self:
            if r.production_lot_id:
                r.product_id = r.production_lot_id.product_id
            else:
                r.product_id = r.product_id
    
    def onchange_category_id_values(self, category_id):
        res = super(AccountAssetAsset, self).onchange_category_id_values(category_id)
        
        if category_id:
            category = self.env['account.asset.category'].browse(category_id)
            res['value'].update({
                'stock_input_account_id': category.stock_input_account_id.id,
                })
        return res
    
    def _prepare_account_move_vals(self, date):
        self.ensure_one()
        res = super(AccountAssetAsset, self)._prepare_account_move_vals(date)
        
        if self.production_lot_id:
            for line in res['line_ids']:
                line[2].update({'product_id': self.production_lot_id.product_id.id})
        return res
    
    @api.onchange('production_lot_id')
    def _onchange_production_lot_id(self):
        if self.production_lot_id:
            self.category_id = self.production_lot_id.product_id.asset_category_id
            self.name = '%s/%s' % (self.production_lot_id.product_id.name, self.production_lot_id.name)
            self.product_id = self.production_lot_id.product_id
    
    def _get_accounting_data_for_asset(self):
        self.ensure_one()
        res = super(AccountAssetAsset, self)._get_accounting_data_for_asset()
        
        if self._context.get('stock_in', False):
            stock_valuation_account_id = self.stock_input_account_id or self.category_id.stock_input_account_id
            if not stock_valuation_account_id:
                raise UserError(_('The following field on Asset Category or on Asset is invalid: Stock Input Account'))
            res.update({'disposal_account_id': stock_valuation_account_id.id})
        return res
    
    def create_stock_move(self, name, location_id, location_dest_id, date):
        stock_move_obj = self.env['stock.move']
        for r in self:
            product_id = self.production_lot_id.product_id.id
            product_qty = abs(self.production_lot_id.product_qty) or 1.0
            product_uom_id = self.production_lot_id.product_uom_id.id
            date = date or fields.Datetime.now()
            move_val = {
                'name': _('%s%s') % (name, r.name.upper().replace(' ', '')),
                'date': date,
                'product_id': product_id,
                'quantity_done': product_qty,
                'product_uom_qty': product_qty,
                'product_uom': product_uom_id,
                'price_unit': r.depreciation_line_ids.sorted(key='depreciation_date')[-1].remaining_value if r.depreciation_line_ids else r.value_residual,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'move_line_ids': [(0, 0, {'account_asset_asset_id': r.id,
                                          'date': date,
                                          'qty_done': product_qty,
                                          'product_id': product_id,
                                         'product_uom_id': product_uom_id,
                                         'location_id': location_id,
                                         'location_dest_id': location_dest_id,
                                         'lot_id': r.production_lot_id.id,
                                         })]
                }
            move_id = stock_move_obj.create(move_val)
            return move_id
    
    def create_account_move(self, post_move=True):
        self.ensure_one()
        res = super(AccountAssetAsset, self).create_account_move(post_move=post_move)
        
        name = False
        date = False
        location_dest_id, location_id = self._get_locations()
        location_id = location_id or self.env.ref('to_stock_asset.stock_location_asset').id
        
        if self._context.get('dispose', False):
            name = 'DISPOSAL/ASSET/'
            location_dest_id = self.env['stock.location'].search([('usage', '=', 'inventory'), ('company_id', '=', self.env.company.id)], limit=1).id
            date = self._context.get('disposed_date', False)
            if date:
                date = datetime.combine(date, fields.Datetime.now().time())
            else:
                date = fields.Datetime.now()
        elif self._context.get('sell', False):
            name = 'SELL/ASSET/'
            location_dest_id = self.env.ref('stock.stock_location_customers').id
            date = self._context.get('sale_date', False)
            if date:
                date = datetime.combine(date, fields.Datetime.now().time())
            else:
                date = fields.Datetime.now()
        elif self._context.get('stock_in', False):
            name = 'STOCK-IN/ASSET/'
            location_dest_id = self._context.get('location_id', False) or location_dest_id
            date = self._context.get('stock_in_date', fields.Datetime.now())
        
        if not location_id or not location_dest_id:
            raise UserError(_('Emptying source location or destination location is not allowed when transfering!'))
        if self.production_lot_id and self._context.get('stock_in', False):
            stock_move_id = self.create_stock_move(name, location_id, location_dest_id, date)
            res.write({
                'stock_move_id': stock_move_id.id,
                'ref': stock_move_id.name,
                'line_ids': [(1, line.id, {
                    'stock_move_id': stock_move_id.id,
                    'name': stock_move_id.name,
                    'quantity': abs(self.production_lot_id.product_qty) or 1.0,
                    }) for line in res.line_ids]
                })
    
    def action_view_sales_invoice(self):
        self.ensure_one()
        res = super(AccountAssetAsset, self).action_view_sales_invoice()
        move_ids = self.mapped('move_ids').filtered(lambda move: move.type == 'out_invoice')

        # choose the view_mode accordingly
        if len(move_ids) <= 1 and self.production_lot_id:
            product_qty = abs(self.production_lot_id.product_qty) or 1.0
            res['context']['default_line_ids'][0][2].update({
                    'product_id': self.production_lot_id.product_id.id,
                    'name': self.production_lot_id.product_id.name,
                    'quantity': product_qty,
                    'price_unit': 0,
                })
        return  res
    
    def action_view_stock_move_lines(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0]
        action['domain'] = [('id', 'in', self.stock_move_line_ids.ids)]
        return action
    
    @api.model
    def _update_production_lot_vals(self, lot, vals):
        can_read = lot.check_access_rights('write', False)
        if can_read:
            lot.write(vals)
        else:
            lot.sudo().write(vals)

    def _update_production_lot_status(self):
        for r in self.filtered(lambda r: r.production_lot_id):
            r._update_production_lot_vals(r.production_lot_id, {'asset_status': r.state})

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountAssetAsset, self).create(vals_list)
        res._update_production_lot_status()
        return res

    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        if 'state' in vals:
            self._update_production_lot_status()
        return res
    
    def unlink(self):
        if not self._context.get('return_picking', False) and self.mapped('stock_move_line_ids'):
            raise UserError(_("You cannot delete asset that is already linked to a stock move line!"))
        
        lots = self.mapped('production_lot_id')
        res = super(AccountAssetAsset, self).unlink()
        
        if lots:
            for lot in lots:
                self._update_production_lot_vals(lot, lot._prepare_production_lot_vals_when_removing_asset())
        return res
