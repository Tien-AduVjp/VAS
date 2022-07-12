from odoo import models, api


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    @api.model
    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        res = super(AccountChartTemplate, self).generate_journals(acc_template_ref, company, journals_dict)
        lcj_journal_id = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('code', '=', 'ITLC'),
            ('company_id', '=', company.id)], limit=1)
        if lcj_journal_id:
            company.write({'landed_cost_journal_id': lcj_journal_id.id})
        return res

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(acc_template_ref, company, journals_dict)
        journal_data.append(company._prepare_landed_cost_journal_data())
        return journal_data
