from odoo import models, api


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _prepare_transfer_account_for_direct_creation(self, name, company):
        vals = super(AccountChartTemplate, self)._prepare_transfer_account_for_direct_creation(name, company)
        if company.chart_template_id.id == self.env.ref('l10n_vn_c133.vn_template_c133').id:
            digits = self.code_digits or 6
            vals.update({
                'code': self.env['account.account']._search_new_account_code(company, digits, '138')
            })
        return vals

    @api.model
    def _get_installed_vietnam_coa_templates(self):
        templates = super(AccountChartTemplate, self)._get_installed_vietnam_coa_templates()
        templates |= self.env.ref('l10n_vn_c133.vn_template_c133')
        return templates
