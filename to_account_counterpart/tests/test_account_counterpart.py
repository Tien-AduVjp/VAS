import datetime

from odoo.tests import tagged
from odoo.tests.common import SingleTransactionCase

from odoo import fields


@tagged('post_install', '-at_install')
class TestAccountCounterpart(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountCounterpart, cls).setUpClass()
        
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
        # Create Partner
        context_no_mail = {'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True}
        Partner = cls.env['res.partner'].with_context(context_no_mail)
        cls.partner1 = Partner.create({
            'name': 'Partner 1',
            'email': 'partner1@example.viindoo.com',
        })
        cls.partner2 = Partner.create({
            'name': 'Partner 2',
            'email': 'partner2@example.viindoo.com',
        })
        cls.partner3 = Partner.create({
            'name': 'Partner 3',
            'email': 'partner3@example.viindoo.com',
        })
        # Create more account
        user_type_liquidity = cls.env.ref('account.data_account_type_liquidity')
        cls.account_1 = cls.env['account.account'].create({
            'code': 'NC1115',
            'name': 'Liquidity Account1',
            'user_type_id': user_type_liquidity.id,
        })
        cls.account_2 = cls.env['account.account'].create({
            'code': 'NC1116',
            'name': 'Liquidity Account2',
            'user_type_id': user_type_liquidity.id,
        })
        cls.account_3 = cls.env['account.account'].create({
            'code': 'NC1117',
            'name': 'Liquidity Account3',
            'user_type_id': user_type_liquidity.id,
        })
        cls.account_4 = cls.env['account.account'].create({
            'code': 'NC1118',
            'name': 'Liquidity Account4',
            'user_type_id': user_type_liquidity.id,
        })
        cls.account_5 = cls.env['account.account'].create({
            'code': 'NC1119',
            'name': 'Liquidity Account5',
            'user_type_id': user_type_liquidity.id,
        })
        cls.account_6 = cls.env['account.account'].create({
            'code': 'NC1120',
            'name': 'Liquidity Account6',
            'user_type_id': user_type_liquidity.id,
        })
        cls.account_7 = cls.env['account.account'].create({
            'code': 'NC1121',
            'name': 'Liquidity Account7',
            'user_type_id': user_type_liquidity.id,
        })
        cls.account_8 = cls.env['account.account'].create({
            'code': 'NC1122',
            'name': 'Liquidity Account8',
            'user_type_id': user_type_liquidity.id,
        })
        
    def _prepare_account_move_line(self, account, debit, credit, amount_currency, currency, partner):
        company = self.env.company
        company_currency = company.currency_id
        if currency and currency != company_currency:
            balance = currency._convert(amount_currency, company_currency, company, fields.Date.today())
            debit = balance > 0 and balance or 0.0
            credit = balance < 0 and -balance or 0.0
        return {
                'account_id': account.id,
                'debit': debit,
                'credit': credit,
                'amount_currency': amount_currency,
                'currency_id': currency.id if currency and currency != company_currency else False,
                'partner_id': partner and partner.id or False
                }
        
    def _create_account_move(self, lines, currency=False):
        """
        lines: [(account1, debit1, credit1, amount_currency1, partner1), (account2, debit2, credit2, amount_currency2, partner2)]
        currency: Currency of account move
        """
        move_lines = []
        for account, debit, credit, amount_currency, partner in lines:
            move_lines.append((0, 0, self._prepare_account_move_line(account, debit, credit, amount_currency, currency, partner)))
        account_move = self.env['account.move'].create({
                                                'type': 'entry',
                                                'line_ids': move_lines,
                                                })
        return account_move
    
    def _check_none_counterpart(self, account_move):
        # Account move
        self.assertFalse(account_move.ctp_ids)
        self.assertEqual(account_move.countered_status, 'none')
        
        # Move lines
        for line in account_move.line_ids:
            self.assertFalse(line.cr_ctp_ids)
            self.assertFalse(line.ctp_aml_ids)
            self.assertFalse(line.dr_ctp_ids)
            self.assertFalse(line.ctp_account_ids)
            self.assertEqual(line.countered_status, 'none')
            self.assertEqual(line.countered_amt, 0.0)
            self.assertEqual(line.countered_amt_currency, 0.0)
    
    def _check_full_counterpart_basic(self, account_move):
        # Account move
        self.assertTrue(account_move.ctp_ids)
        self.assertEqual(account_move.countered_status, 'fully')
        self.assertEqual(account_move.ctp_ids, account_move.line_ids.mapped('ctp_ids'))
        
        # Move lines
        for line in account_move.line_ids:
            self.assertTrue(line.ctp_aml_ids)
            self.assertTrue(line.ctp_ids)
            self.assertEqual(line.countered_status, 'fully')
        
    # Base currency of company: EURO
    #============================== 
    def test_01_account_move_1_1_currency_euro(self):
        lines = [(self.account_1, 139.0, 0.0, 0.0, False),
                 (self.account_2, 0.0, 139.0, 0.0, False)]
        
        account_move = self._create_account_move(lines)
        self._check_none_counterpart(account_move)
        account_move.post()
        move_lines = account_move.line_ids
        # basic test
        self._check_full_counterpart_basic(account_move)
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[1].id, 'countered_amt': 139.0},
        ])
        # Set to draft to remove counterpart
        account_move.button_draft()
        self._check_none_counterpart(account_move)
        
    def test_02_account_move_1_2_currency_euro(self):
        lines = [(self.account_1, 139.0, 0.0, 0.0, False),
                (self.account_2, 0.0, 100.0, 0.0, False),
                (self.account_3, 0.0, 39.0, 0.0, False)]
        
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[1].id, 'countered_amt': 100.0},
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[2].id, 'countered_amt': 39.0},
        ])
        
    def test_03_account_move_2_1_currency_euro(self):
        lines = [(self.account_1, 100.0, 0.0, 0.0, False),
                 (self.account_2, 39.0, 0.0, 0.0, False),
                 (self.account_3, 0.0, 139.0, 0.0, False)]
        
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[2].id, 'countered_amt': 100.0},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[2].id, 'countered_amt': 39.0},
        ])
        
    def test_04_account_move_2_2_currency_euro(self):
        lines = [(self.account_1, 100.0, 0.0, 0.0, False),
                 (self.account_2, 39.0, 0.0, 0.0, False),
                 (self.account_3, 0.0, 45.0, 0.0, False),
                 (self.account_4, 0.0, 94.0, 0.0, False)]
        
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[2].id, 'countered_amt': 32.37},
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 67.63},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[2].id, 'countered_amt': 12.63},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 26.37},
        ])
        
    def test_05_account_move_2_2_currency_usd(self):
        lines = [(self.account_1, 0.0, 0.0, 100.0, False),
                 (self.account_2, 0.0, 0.0, 39.0, False),
                 (self.account_3, 0.0, 0.0, -45.0, False),
                 (self.account_4, 0.0, 0.0, -94.0, False)]
        
        account_move = self._create_account_move(lines, self.currency_usd)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[2].id, 'countered_amt': 36.17, 'countered_amt_currency': 32.37},
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 75.56, 'countered_amt_currency': 67.63},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[2].id, 'countered_amt': 14.11, 'countered_amt_currency': 12.63},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 29.47, 'countered_amt_currency': 26.37},
        ])
    
    def test_06_account_move_3_3_same_amount_same_partner(self):
        lines = [(self.account_1, 100.0, 0.0, 0.0, self.partner1),
                 (self.account_2, 39.0, 0.0, 0.0, self.partner3),
                 (self.account_3, 50.0, 0.0, 0.0, self.partner2),
                 (self.account_5, 0.0, 39.0, 0.0, self.partner3),
                 (self.account_4, 0.0, 50.0, 0.0, self.partner2),
                 (self.account_6, 0.0, 100.0, 0.0, self.partner1)]
        
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 100.0},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 39.0},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[4].id, 'countered_amt': 50.0},
        ])
    
    def test_07_account_move_3_3_same_amount_no_partner(self):
        lines = [(self.account_1, 100.0, 0.0, 0.0, False),
                 (self.account_2, 39.0, 0.0, 0.0, False),
                 (self.account_3, 50.0, 0.0, 0.0, False),
                 (self.account_4, 0.0, 39.0, 0.0, False),
                 (self.account_5, 0.0, 50.0, 0.0, False),
                 (self.account_6, 0.0, 100.0, 0.0, False)]
        
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 100.0},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 39.0},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[4].id, 'countered_amt': 50.0},
        ])
        
    def test_08_account_move_3_3_same_amount_diff_partner(self):
        lines = [(self.account_1, 100.0, 0.0, 0.0, self.partner1),
                 (self.account_2, 39.0, 0.0, 0.0, self.partner2),
                 (self.account_3, 50.0, 0.0, 0.0, self.partner3),
                 (self.account_4, 0.0, 39.0, 0.0, self.partner3),
                 (self.account_5, 0.0, 50.0, 0.0, self.partner1),
                 (self.account_6, 0.0, 100.0, 0.0, self.partner2)]
         
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[4].id, 'countered_amt': 50.0},
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 50.0},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 39.0},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 39.0},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 11.0},
        ])
    
    def test_09_account_move_3_3_diff_amount_no_partner(self):
        lines = [(self.account_1, 100.0, 0.0, 0.0, False),
                 (self.account_2, 39.0, 0.0, 0.0, False),
                 (self.account_3, 50.0, 0.0, 0.0, False),
                 (self.account_4, 0.0, 29.0, 0.0, False),
                 (self.account_5, 0.0, 70.0, 0.0, False),
                 (self.account_6, 0.0, 90.0, 0.0, False)]
        
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # Counterpart lines test
        # countered_amt = (dr_aml_id.debit / sum(debit_line_ids.mapped('debit'))) * cr_aml_id.credit
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 15.34},
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[4].id, 'countered_amt': 37.04},
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 47.62},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 5.99},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[4].id, 'countered_amt': 14.44},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 18.57},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[3].id, 'countered_amt': 7.67},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[4].id, 'countered_amt': 18.52},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 23.81},
        ])
        
    def test_10_account_move_4_4_diff_amount_has_partner(self):
        lines = [(self.account_1, 100.0, 0.0, 0.0, self.partner1),
                 (self.account_2, 39.0, 0.0, 0.0, False),
                 (self.account_3, 50.0, 0.0, 0.0, self.partner2),
                 (self.account_4, 20.0, 0.0, 0.0, False),
                 (self.account_5, 0.0, 29.0, 0.0, False),
                 (self.account_6, 0.0, 80.0, 0.0, self.partner1),
                 (self.account_7, 0.0, 90.0, 0.0, self.partner2),
                 (self.account_8, 0.0, 10.0, 0.0, False)]
        
        account_move = self._create_account_move(lines)
        account_move.post()
        move_lines = account_move.line_ids
        # basic test
        self._check_full_counterpart_basic(account_move)
        # Counterpart lines test
        self.assertRecordValues(account_move.ctp_ids, [
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[5].id, 'countered_amt': 80.0},
            {'dr_aml_id': move_lines[0].id, 'cr_aml_id': move_lines[6].id, 'countered_amt': 20.0},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[4].id, 'countered_amt': 29.0},
            {'dr_aml_id': move_lines[1].id, 'cr_aml_id': move_lines[7].id, 'countered_amt': 10.0},
            {'dr_aml_id': move_lines[2].id, 'cr_aml_id': move_lines[6].id, 'countered_amt': 50.0},
            {'dr_aml_id': move_lines[3].id, 'cr_aml_id': move_lines[6].id, 'countered_amt': 20.0},
        ])
        # Set to draft to remove counterpart
        account_move.button_draft()
        self._check_none_counterpart(account_move)
       
