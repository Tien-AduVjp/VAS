from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _create_bank_journals(self, company, acc_template_ref):
        bank_journals = super(AccountChartTemplate, self)._create_bank_journals(company, acc_template_ref)

        # If the company's country is in the list of the country codes of the countries for which,
        # by default, payments made on bank journals should be creating draft account.move objects,
        # which get in turn posted when their payment gets reconciled with a bank statement line.
        if company.country_id.code in self.get_countries_posting_at_bank_rec():
            bank_journals.write({'post_at': 'bank_rec'})
        return bank_journals
