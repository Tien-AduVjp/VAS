from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_journal_cash_suspense_account_id = fields.Many2one('account.account', string='Journal Cash Suspense Account')
    unemployment_insurance_account_id = fields.Many2one('account.account', string='Unemployment Insurance account')

    def _disable_anglo_saxon_for_vn_coa(self):
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        companies = self.search([('chart_template_id', 'in', vn_charts.ids), ('anglo_saxon_accounting', '=', True)])
        if companies:
            companies.write({'anglo_saxon_accounting': False})

    def _filter_vietnam_coa(self):
        """
        Filter the companies having Vietnam CoA (TT200 / TT133) in self
        """
        vn_coa = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        return self.filtered(lambda c: c.chart_template_id and c.chart_template_id in vn_coa)
