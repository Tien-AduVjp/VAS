from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAssetAssetAddWizard(models.TransientModel):
    _name = 'asset.fill.missing.values.wizard'
    _description = 'Fill missing values to Asset'


    first_depreciation_date = fields.Date(
        string='First Depreciation Date',
        help='Note that this date does not alter the computation of the first journal entry in case of prorata temporis assets. It simply changes its accounting date'
        )
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', groups='analytic.group_analytic_accounting')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', groups='analytic.group_analytic_tags')

    @api.model
    def default_get(self, fields_list):
        res = super(AccountAssetAssetAddWizard, self).default_get(fields_list)
        asset_id = self.env.context.get('active_id')
        asset = self.env['account.asset.asset'].browse(asset_id)
        if not asset:
            raise UserError(_("No asset found!"))
        if 'first_depreciation_date' in fields_list:
            res.update({'first_depreciation_date': asset.first_depreciation_date})
        if 'analytic_account_id' in fields_list and self.env.user.has_group('analytic.group_analytic_accounting'):
            res.update({'analytic_account_id': asset.sudo().analytic_account_id.id})
        if 'analytic_tag_ids' in fields_list and self.env.user.has_group('analytic.group_analytic_tags'):
            res.update({'analytic_tag_ids': [(6, 0, asset.sudo().analytic_tag_ids.ids)]})
        return res

    def _prepare_account_asset_vals(self):
        self.ensure_one()
        vals = {}
        if self.first_depreciation_date:
            vals.update({
                'first_depreciation_date': self.first_depreciation_date,
            })
        if self.sudo().analytic_account_id:
            vals.update({
                'analytic_account_id': self.analytic_account_id.id,
            })
        if self.sudo().analytic_tag_ids:
            vals.update({
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            })
        return vals

    def _update_account_asset_vals(self, asset_id):
        asset_vals = self._prepare_account_asset_vals()
        if asset_vals:
            can_write = asset_id.check_access_rights('write', False)
            asset_id = can_write and asset_id or asset_id.sudo()

            asset_id.write(asset_vals)

    def action_fill_missing_values(self):
        self.ensure_one()
        asset_ids = self._context.get('active_ids', False)
        if len(asset_ids) > 1:
            raise UserError(_('You may only fill missing values to one asset at a time!'))

        asset_id = self.env['account.asset.asset'].browse(asset_ids)
        if asset_id and asset_id.state not in ['draft', 'open']:
            raise UserError(_('You may only fill missing values to one asset that in draft / open state!'))
        self._update_account_asset_vals(asset_id)
