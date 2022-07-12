from odoo import models, fields, api

class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    @api.model
    def _prepare_transfer_account_for_direct_creation(self, name, company):
        vals = super(AccountChartTemplate, self)._prepare_transfer_account_for_direct_creation(name, company)
        vn_chart_of_account_c133 = self.env.ref('l10n_vn_c133.vn_template_c133')
        if self == vn_chart_of_account_c133:
            digits = self.code_digits or 6
            prefix = '138'
            vals.update({
                'code': self.env['account.account']._search_new_account_code(company, digits, prefix)
                })
        return vals

    def generate_account(self, tax_template_ref, acc_template_ref, code_digits, company):
        acc_template_ref = super(AccountChartTemplate, self).generate_account(tax_template_ref, acc_template_ref, code_digits, company)
        vn_chart_of_account_c133 = self.env.ref('l10n_vn_c133.vn_template_c133')
        if self == vn_chart_of_account_c133:
            transfer_account_template = self.env['account.account.template'].search([
                ('code', '=like', self.transfer_account_code_prefix + '%'), ('chart_template_id', '=', self.id)])
            transfer_account = self.env['account.account'].search([('code', 'in', transfer_account_template.mapped('code')), ('company_id', '=', company.id)])
            if transfer_account:
                transfer_account.write({'deprecated': True})
        return acc_template_ref
