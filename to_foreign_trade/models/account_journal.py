from odoo import models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def create_imex_tax_journals(self):
        Journal = self.env['account.journal']
        for company in self.env['res.company'].search([('chart_template_id', '!=', False)]):
            journal_id = Journal.search([('code', '=', 'CDJ'), ('company_id', '=', company.id)], limit=1)
            if not journal_id:
                journal_id = Journal.create(company._prepare_imex_tax_journal_data())
            company.write({'account_journal_custom_clearance': journal_id.id})
