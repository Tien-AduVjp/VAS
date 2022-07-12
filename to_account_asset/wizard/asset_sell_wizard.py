from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetSellWizard(models.TransientModel):
    _name = 'asset.sell.wizard'
    _description = 'Asset Sell Wizard'


    asset_id = fields.Many2one('account.asset.asset', string='Asset', readonly=True, required=True)
    stopped_depreciating_date = fields.Date(
        string='Stopped Depreciating Date',
        help='Note that this date simply uses as last depreciation date',
        default=fields.Date.today,
        required=True
        )
    sale_date = fields.Date(
        string='Sales Invoice Date',
        help='Note that this date simply uses its invoice date',
        default=fields.Date.today
        )

    def action_sell(self):
        self.ensure_one()
        asset_ids = self._context.get('active_ids', False)
        if len(asset_ids) > 1:
            raise UserError(_('You may only sell one asset at a time'))

        first_depreciation_date = self.asset_id.date_first_depreciation == 'manual' and self.asset_id.first_depreciation_date or self.asset_id.date
        if self.stopped_depreciating_date < first_depreciation_date:
            raise UserError(_('The stopped depreciating date cannot be set before first depreciation date!'))
        if self.sale_date and self.sale_date < first_depreciation_date:
            raise UserError(_('The sales invoice date cannot be set before first depreciation date!'))
        return self.asset_id.with_context(stopped_depreciating_date=self.stopped_depreciating_date, sale_date=self.sale_date).button_sell()
