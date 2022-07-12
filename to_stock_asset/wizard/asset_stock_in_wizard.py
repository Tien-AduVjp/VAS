from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetStockInWizard(models.TransientModel):
    _name = 'asset.stock.in.wizard'
    _description = 'Asset Stock In'

    asset_id = fields.Many2one('account.asset.asset', string='Asset', readonly=True, required=True)
    date = fields.Datetime(string='Date of Transfer', default=fields.Datetime.now, required=True,
                           help="Date at which the transfer has been processed or cancelled.")
    location_id = fields.Many2one('stock.location', 'Stock-in Location', domain="[('usage', '=', 'internal')]",
                                  required=True, groups="stock.group_stock_multi_locations")

    @api.model
    def default_get(self, fields_list):
        assets = self.env.context.get('active_ids', [])
        if not assets or len(assets) > 1:
            raise UserError(_("You may only stock-in one asset at a time."))
        res = super(AssetStockInWizard, self).default_get(fields_list)
        asset = self.env['account.asset.asset'].browse(assets)
        location_id, location_dest_id = asset._get_locations()
        res['location_id'] = location_id
        res['asset_id'] = assets[0]
        return res

    def create_asset_stock_in(self):
        self.ensure_one()
        if not self.asset_id.production_lot_id:
            raise UserError(_("Emptying the Lot/Serial Number is not allowed when transfering!"))

        move_line_old_ids = self.env['stock.move.line'].search([
                ('state', '=', 'done'),
                ('lot_id', '=', self.asset_id.production_lot_id.id)])\
                .filtered(lambda line: line.location_dest_id.usage == 'internal')
        dates = move_line_old_ids.mapped('date')
        if dates:
            date = max(dates)
            if date > self.date:
                raise UserError(_("The Date of Transfer cannot be set before purchase date/stock input date!"))
        self.asset_id.with_context(stock_in=True, location_id=self.sudo().location_id.id, stock_in_date=self.date).button_dispose()
