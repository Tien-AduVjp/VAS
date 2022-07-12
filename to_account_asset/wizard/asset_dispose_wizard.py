from odoo import fields, models, _
from odoo.exceptions import UserError


class AssetDisposalWizard(models.TransientModel):
    _name = 'asset.dispose.wizard'
    _description = 'Asset Dispose Wizard'


    asset_id = fields.Many2one('account.asset.asset', string='Asset', readonly=True, required=True)
    disposed_date = fields.Date(
        string='Disposed Date',
        help='Note that this date simply uses as disposed date',
        default=fields.Date.today,
        required=True
        )

    def action_dispose(self):
        self.ensure_one()
        asset_ids = self._context.get('active_ids', False)
        if len(asset_ids) > 1:
            raise UserError(_('You may only dispose one asset at a time'))
        first_depreciation_date = self.asset_id.date_first_depreciation == 'manual' and self.asset_id.first_depreciation_date or self.asset_id.date
        if self.disposed_date < first_depreciation_date:
            raise UserError(_('The disposed date cannot be set before first depreciation date!'))
        return self.asset_id.with_context(disposed_date=self.disposed_date, dispose=True).button_dispose()
