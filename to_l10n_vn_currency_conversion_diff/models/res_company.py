from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_currency_conversion_diff_accounts(self):
        """
        Override for Vietnam companies
        """
        vietnam_coa = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if vietnam_coa and self.chart_template_id.id in vietnam_coa.ids:
            income_account = self.env['account.account'].search([
                ('company_id', '=', self.id),
                ('code', 'ilike', '711' + '%')], limit=1)
            expense_account = self.env['account.account'].search([
                ('company_id', '=', self.id),
                ('code', 'ilike', '811' + '%')], limit=1)
            return income_account, expense_account
        return super(ResCompany, self)._get_currency_conversion_diff_accounts()
