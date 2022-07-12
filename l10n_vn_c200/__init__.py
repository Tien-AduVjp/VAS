from odoo import api, SUPERUSER_ID
from . import models


def _handle_data_vietnam_coa(env):
    """
    Handle data for companies that have previously installed VietNam COA template
    """
    # With the companies have installed Vietnam coa template, change the outstanding account's name and code
    # Exp:
    # In journal Bank/Cash
    # [Bank Journal      Bank Account: 1125 Bank]
    # Before:
    #     Outstanding Receipts Account: [Code] Outstanding Receipts
    #     [1126 Outstanding Receipts]
    #     Outstanding Payments Account: [Code] Outstanding Payments
    #     [1127 Outstanding Payments]
    # After:
    #     Outstanding Receipts Account: [Bank/Cash Account Code]-01 Outstanding Receipts [Journal Name]
    #     [1125-01 Outstanding Receipts (Bank Journal)]
    #     Outstanding Payments Account: [Bank/Cash Account Code]-02 Outstanding Payments [Journal Name]
    #     [1125-02 Outstanding Payments (Bank Journal)]
    companies = env['res.company'].with_context(active_test=False).search([('chart_template_id', '=', env.ref('l10n_vn.vn_template').id)])
    bank_cash_journals = env['account.journal'].search([('company_id', 'in', companies.ids), ('type', 'in', ('bank', 'cash'))])
    for journal in bank_cash_journals:
        journal_name = ' (%s)' % journal.name
        if journal.default_account_id and journal.payment_debit_account_id and journal.payment_credit_account_id:
            journal.payment_debit_account_id.write({
                'code': journal.default_account_id.code + '-01',
                'name': journal.payment_debit_account_id.name + journal_name,
            })
            journal.payment_credit_account_id.write({
                'code': journal.default_account_id.code + '-02',
                'name': journal.payment_credit_account_id.name + journal_name,
            })
    bank_cash_journals.flush()


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _handle_data_vietnam_coa(env)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company']._fix_vietnam_coa()
