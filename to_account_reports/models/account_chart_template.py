from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _get_account_vals(self, company, account_template, code_acc, tax_template_ref):
        self.ensure_one()
        vals = super(AccountChartTemplate, self)._get_account_vals(company, account_template, code_acc, tax_template_ref)
        vals.update({
            'show_both_dr_and_cr_trial_balance': account_template.show_both_dr_and_cr_trial_balance
            })
        return vals

