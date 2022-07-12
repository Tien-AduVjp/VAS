from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_asset_allocation = fields.Boolean(compute='_compute_is_asset_allocation',
                                         help="A technical field to show/hide Assets button box.")

    @api.depends('picking_type_id')
    def _compute_is_asset_allocation(self):
        for r in self:
            if r.location_dest_id.usage == 'asset_allocation':
                r.is_asset_allocation = True
            else:
                r.is_asset_allocation = False

    def action_view_account_assets(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_account_asset.action_account_asset_asset')
        action['domain'] = [('id', 'in', self.move_line_ids.mapped('account_asset_asset_id').ids)]
        return action

    def button_validate(self):
        for r in self:
            if r.picking_type_id.code == 'asset_allocation':
                if r.location_id.usage != 'asset_allocation' and r.location_dest_id.usage != 'asset_allocation':
                    raise UserError(_("Source Location or Destination Location of the transfer with this operation type must be configured in Location Type 'Asset Allocation'."))
                for move_line in r.move_line_ids:
                    product = move_line.product_id
                    lot = move_line.lot_id
                    location = move_line.location_id
                    qty_available = product.with_context(location=location.id, lot_id=lot.id).qty_available
                    if float_compare(qty_available, 0, precision_digits=2) != 1:
                        raise UserError(_("No quantity available in stock with Lots/Serial Numbers '%s'!") % lot.name)
    
                for line in r.move_lines:
                    # No require asset category when returning a stock picking that contains assets
                    if line.location_id.usage == 'asset_allocation' and line._is_in() and line.origin_returned_move_id:
                        continue
                    if not line.asset_category_id:
                        raise UserError(_('The following field on Product is invalid: Asset Type'))
    
                for product in r.mapped('move_lines.product_id') | r.mapped('move_line_ids.product_id'):
                    if product.tracking == 'none':
                        raise UserError(_("Please enable Product Traceability on %s product!") % product.name)
                    if product.valuation != 'real_time':
                        raise UserError(_("The product '%(product)s' of the transfer '%(picking)s' must be configured in "\
                                          "automated valuation method!", product=product.name, picking=r.name))
    
                move_line_ids = r.move_line_ids
                move_line_old_ids = r.env['stock.move.line'].search([
                    ('id', 'not in', move_line_ids.ids),
                    ('state', '=', 'done'),
                    ('lot_id', 'in', move_line_ids.mapped('lot_id').ids)
                    ]).filtered(lambda line: line.location_dest_id.usage == 'internal')
    
                for line in move_line_ids:
                    move_line_by_lots = move_line_old_ids.filtered(lambda move_line: move_line.lot_id == line.lot_id)
                    dates = move_line_by_lots.mapped('date')
                    if dates:
                        date = max(dates)
                        if date > line.date:
                            raise UserError(_("The Expected Date cannot be set before purchase date/stock input date!"))
                    move_line_old_ids -= move_line_by_lots
        return super(StockPicking, self).button_validate()
