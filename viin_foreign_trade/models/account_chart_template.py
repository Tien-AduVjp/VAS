from odoo import models, api


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    @api.model
    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        res = super(AccountChartTemplate, self).generate_journals(acc_template_ref, company, journals_dict)
        cdj_journal_id = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('code', '=', 'CDJ'),
            ('company_id', '=', company.id)], limit=1)
        if cdj_journal_id:
            company.write({'account_journal_custom_clearance': cdj_journal_id.id})

        lcj_journal_id = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('code', '=', 'ITLC'),
            ('company_id', '=', company.id)], limit=1)
        if lcj_journal_id:
            company.write({'landed_cost_journal_id': lcj_journal_id.id})
        return res

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(acc_template_ref, company, journals_dict)
        journal_data.append(company._prepare_imex_tax_journal_data())
        journal_data.append(company._prepare_landed_cost_journal_data())
        return journal_data
