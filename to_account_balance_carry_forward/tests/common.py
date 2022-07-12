import datetime
from datetime import date
from odoo.tests.common import SingleTransactionCase
from odoo import fields


class Common(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_euro = cls.env.ref("base.EUR")
        cls.currency_usd.decimal_places = 2
        cls.currency_euro.decimal_places = 2
        # Base currency of company: EURO
        cls.cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", [cls.currency_euro.id, cls.env.company.id])
        cls.env['res.currency.rate'].search([]).unlink()
        cls.env['res.currency.rate'].create([{
            'name': fields.Date.today() - datetime.timedelta(days=1),
            'rate': 1,
            'currency_id': cls.currency_euro.id
        },
        {
            'name': fields.Date.today() - datetime.timedelta(days=1),
            'rate': 0.895,
            'currency_id': cls.currency_usd.id
        }])
        # Create Company
        cls.company2 = cls.env['res.company'].create({'name': 'Company2'})
        # Create Journal
        cls.journal_bcf = cls.env['account.journal'].create({
            'name': 'BCF Journal',
            'code': 'BCFJ',
            'type': 'general',
            'company_id': cls.env.company.id,
        })
        # Create accounts
        user_type_receivable = cls.env.ref('account.data_account_type_receivable')
        cls.account_131 = cls.env['account.account'].create({
            'code': 'NC131',
            'name': 'Receivable Account 131',
            'user_type_id': user_type_receivable.id,
            'reconcile': True,
        })
        user_type_revenue = cls.env.ref('account.data_account_type_revenue')
        cls.account_5111 = cls.env['account.account'].create({
            'code': 'NC5111',
            'name': 'Revenue Account 5111',
            'user_type_id': user_type_revenue.id,
        })
        cls.account_5112 = cls.env['account.account'].create({
            'code': 'NC5112',
            'name': 'Revenue Account 5112',
            'user_type_id': user_type_revenue.id,
        })
        cls.account_521 = cls.env['account.account'].create({
            'code': 'NC521',
            'name': 'Revenue Account 521',
            'user_type_id': user_type_revenue.id,
        })
        cls.account_company2 = cls.env['account.account'].create({
            'code': 'COM2_NCCOMP2',
            'name': 'Revenue Account COMP2',
            'user_type_id': user_type_revenue.id,
            'company_id': cls.company2.id,
        })
        user_type_unaffected_earnings = cls.env.ref('account.data_unaffected_earnings')
        cls.account_911 = cls.env['account.account'].search([('user_type_id', '=', user_type_unaffected_earnings.id)], limit=1)
        if not cls.account_911:
            cls.account_911 = cls.env['account.account'].create({
                'code': 'NC911',
                'name': 'Current Year Earnings 911',
                'user_type_id': user_type_unaffected_earnings.id,
            })
        user_type_equity = cls.env.ref('account.data_account_type_equity')
        cls.account_4212 = cls.env['account.account'].create({
            'code': 'NC4212',
            'name': 'Equity Account 4212',
            'user_type_id': user_type_equity.id,
        })
        # Create Balance Carry Forward Rules
        cls.env['balance.carry.forward.rule'].search([]).unlink()
        cls.rule_521_to_5111 = cls.env['balance.carry.forward.rule'].create({
            'name': '521->5111',
            'source_account_ids': [(6, 0, [cls.account_521.id])],
            'dest_account_id': cls.account_5111.id,
            'profit_loss': False,
            'sequence': 10,
        })
        cls.rule_511_to_911 = cls.env['balance.carry.forward.rule'].create({
            'name': '511->911',
            'source_account_ids': [(6, 0, [cls.account_5111.id, cls.account_5112.id])],
            'dest_account_id': cls.account_911.id,
            'profit_loss': False,
            'sequence': 5,
        })
        # Create Journal Entries to set balance for accounts
        cls.move1 = cls.env['account.move'].create({
            'type': 'entry',
            'date': date(2021, 8, 20),
            'line_ids': [(0, 0, {'account_id': cls.account_131.id, 'debit': 1000.0, 'credit': 0.0, }),
                         (0, 0, {'account_id': cls.account_5111.id, 'debit': 0.0, 'credit': 1000.0})]
        })
        cls.move1.post()
        cls.move2 = cls.env['account.move'].create({
            'type': 'entry',
            'date': date(2021, 8, 23),
            'line_ids': [(0, 0, {'account_id': cls.account_521.id, 'debit': 300.0, 'credit': 0.0, }),
                         (0, 0, {'account_id': cls.account_131.id, 'debit': 0.0, 'credit': 300.0})]
        })
        cls.move2.post()

