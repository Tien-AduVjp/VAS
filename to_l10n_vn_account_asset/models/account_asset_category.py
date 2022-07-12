from odoo import api, models


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'
    
    @api.model
    def _get_default_analytic_tags(self):
        """
        For future potential inheritance
        """
        return self.env.ref('l10n_vn_c200.analytic_tag_fixed_assets') + super(AccountAssetCategory, self)._get_default_analytic_tags()

    @api.model
    def _get_default_revaluation_decrease_account_id(self):
        if self.env.company.chart_template_id == self.env.ref('l10n_vn.vn_template'):
            return self.env['account.account'].search([('code', '=', '412')], limit=1)
        return super(AccountAssetCategory, self)._get_default_revaluation_decrease_account_id()

    @api.model
    def _get_default_revaluation_increase_account_id(self):
        if self.env.company.chart_template_id == self.env.ref('l10n_vn.vn_template'):
            return self.env['account.account'].search([('code', '=', '412')], limit=1)
        return super(AccountAssetCategory, self)._get_default_revaluation_increase_account_id()
