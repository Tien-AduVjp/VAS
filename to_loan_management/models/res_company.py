import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class res_company(models.Model):
    _inherit = "res.company"

    loan_borrowing_journal_id = fields.Many2one('account.journal', string='Borrowing Journal')
    loan_borrowing_account_id = fields.Many2one('account.account', string='Loan Borrowing Account')
    loan_lending_journal_id = fields.Many2one('account.journal', string='Lending Journal')
    loan_lending_account_id = fields.Many2one('account.account', string='Loan Lending Account')

    def _prepare_borrowing_loan_journal_data(self):
        types = self.env.ref('account.data_account_type_current_liabilities') \
            | self.env.ref('account.data_account_type_non_current_liabilities') \
            | self.env.ref('account.data_account_type_expenses') \
            | self.env.ref('account.data_account_type_payable')
        return {
            'name': _('Borrowing Loans Journal'),
            'type': 'purchase',
            'code': 'BLJ',
            'show_on_dashboard': True,
            'sequence': 12,
            'company_id':self.id,
            'type_control_ids': [(6,0,types.ids)]
            }

    def _prepare_lending_loan_journal_data(self):
        types = self.env.ref('account.data_account_type_current_assets') \
            | self.env.ref('account.data_account_type_non_current_assets') \
            | self.env.ref('account.data_account_type_revenue') \
            | self.env.ref('account.data_account_type_receivable')
        return {
            'name': _('Lending Loans Journal'),
            'type': 'sale',
            'code': 'LLJ',
            'show_on_dashboard': True,
            'sequence': 13,
            'company_id':self.id,
            'type_control_ids': [(6,0,types.ids)]
            }

    @api.model
    def _post_install(self):
        for company_id in self.search([('chart_template_id', '!=', False)]):
            AccountJournal = self.env['account.journal']

            journal_blj_id = AccountJournal.search([
                    ('company_id', '=', company_id.id),
                    ('type', '=', 'purchase'),
                    '|', ('code', '=', 'BLJ'), ('name', 'ilike', "%" + _('Borrowing Loans Journal') + "%")], limit=1)
            if not journal_blj_id:
                val = self._prepare_borrowing_loan_journal_data()
                val['company_id'] = company_id.id
                journal_id = AccountJournal.create(val)
                _logger.info("Journal %s (ID: %s) has been created for the company %s", _('Borrowing Loans Journal'), journal_id.id, company_id.name)


            journal_llj_id = AccountJournal.search([
                    ('company_id', '=', company_id.id),
                    ('type', '=', 'sale'),
                    '|', ('code', '=', 'LLJ'), ('name', 'ilike', "%" + _('Lending Loans Journal') + "%")], limit=1)
            if not journal_llj_id:
                    val = self._prepare_lending_loan_journal_data()
                    val['company_id'] = company_id.id
                    journal_id = AccountJournal.create(val)
                    _logger.info("Journal %s (ID: %s) has been created for the company %s", _('Lending Loans Journal'), journal_id.id, company_id.name)
