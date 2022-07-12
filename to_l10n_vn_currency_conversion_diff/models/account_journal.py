from odoo import models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def _update_currency_conversion_difference_journal_account(self):
        vn_chart_template = self.env.ref('l10n_vn.vn_template', False)
        if vn_chart_template:
            for company in self.env['res.company'].search([('chart_template_id', '=', vn_chart_template.id)]).sudo():
                if company.currency_conversion_diff_journal_id:
                    journal = company.currency_conversion_diff_journal_id
                else:
                    journal = self.env['account.journal'].search([('code', '=', 'CCDJ'), ('company_id', '=', company.id)], limit=1)
                if not journal:
                    continue

                debit_account = self.env['account.account'].search([('code', 'ilike', '811' + '%'), ('company_id', '=', company.id)], limit=1)
                credit_account = self.env['account.account'].search([('code', 'ilike', '711' + '%'), ('company_id', '=', company.id)], limit=1)

                update_data = {}

                if debit_account and (not journal.default_debit_account_id or not journal.default_debit_account_id.code.startswith('811')):
                    update_data['default_debit_account_id'] = debit_account.id
                
                if credit_account and (not journal.default_credit_account_id or not journal.default_credit_account_id.code.startswith('711')):
                    update_data['default_credit_account_id'] = credit_account.id
                
                if bool(update_data):
                    journal.write(update_data)

