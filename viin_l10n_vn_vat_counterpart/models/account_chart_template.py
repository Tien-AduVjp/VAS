from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def generate_properties(self, acc_template_ref, company):
        res = super(AccountChartTemplate, self).generate_properties(acc_template_ref=acc_template_ref, company=company)
        account = getattr(self, 'property_vat_ctp_account_id')
        value = account and acc_template_ref[account.id] or False
        if value:
            company.write({'property_vat_ctp_account_id': value})
        return res
