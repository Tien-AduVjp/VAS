from odoo import api, models


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    @api.model
    def _get_default_analytic_tags(self):
        """
        For future potential inheritance
        """
        return self.env.ref('l10n_vn_common.account_analytic_tag_fixed_assets')\
                | super(AccountAssetCategory, self)._get_default_analytic_tags()

    @api.onchange('asset_account_id')
    def _onchange_account_asset(self):
        res = super(AccountAssetCategory, self)._onchange_account_asset()

        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if self.company_id.chart_template_id.id in vn_charts.ids:
            if self.asset_account_id and self.asset_account_id.code.startswith('211'):

                self.analytic_tag_ids = [(4, self.env.ref('l10n_vn_common.account_analytic_tag_fixed_assets').id)]

                account214 = self.env['account.account'].search([
                    ('code', '=ilike', '214' + '%'),
                    ('company_id', '=', self.company_id.id)
                    ], limit=1)
                self.depreciation_account_id = account214.id
            else:
                self.analytic_tag_ids = [(3, self.env.ref('l10n_vn_common.account_analytic_tag_fixed_assets').id)]
        return res

    @api.model
    def _get_default_revaluation_decrease_account_id(self):
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if self.env.company.chart_template_id.id in vn_charts.ids:
            return self.env['account.account'].search([
                ('code', '=', '412'),
                ('company_id', '=', self.env.company.id)], limit=1)
        return super(AccountAssetCategory, self)._get_default_revaluation_decrease_account_id()

    @api.model
    def _get_default_revaluation_increase_account_id(self):
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if self.env.company.chart_template_id.id in vn_charts.ids:
            return self.env['account.account'].search([
                ('code', '=', '412'),
                ('company_id', '=', self.env.company.id)], limit=1)
        return super(AccountAssetCategory, self)._get_default_revaluation_increase_account_id()

    @api.model
    def _get_default_disposal_expense_account_id(self):
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if self.env.company.chart_template_id.id in vn_charts.ids:
            return self.env['account.account'].search([
                ('code', '=', '811'),
                ('company_id', '=', self.env.company.id)], limit=1)
        return super(AccountAssetCategory, self)._get_default_disposal_expense_account_id()
