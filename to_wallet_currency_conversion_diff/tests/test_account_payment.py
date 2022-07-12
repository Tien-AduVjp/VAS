import datetime

from odoo.tests import SavepointCase, tagged

@tagged('post_install', '-at_install')
class TestAccountPayment(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SavepointCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_eur = cls.env.ref('base.EUR')
        cls.currency_vnd = cls.env.ref('base.VND')

        Rate = cls.env['res.currency.rate']
        cls.currency_usd.rate_ids = Rate.create({
            'name': datetime.date(2020, 1, 1),
            'currency_id': cls.currency_usd.id,
            'rate': 1.1
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Ngoc'
        })
        cls.country_us = cls.env.ref('base.us')
        cls.country_vn = cls.env.ref('base.vn')

        cls.bank_journal_usd = cls.env['account.journal'].create({
            'name': 'Bank USD',
            'type': 'bank',
            'code': 'BNK0123456789',
            'currency_id': cls.currency_usd.id
        })

        cls.bank_journal_vn = cls.env['account.journal'].create({
            'name': 'Bank VND',
            'type': 'bank',
            'code': 'BNK9876543210',
            'currency_id': cls.currency_vnd.id
        })

        cls.account_711 = cls.env['account.account'].create({
            'name': 'Thu nhap khac',
            'code': 711001,
            'user_type_id': cls.env.ref('account.data_account_type_other_income').id,
        })
        cls.account_811 = cls.env['account.account'].create({
            'name': 'Chi phi khac',
            'code': 811001,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
        })
        cls.conversion_diff_journal = cls.env['account.journal'].create({
            'name': 'Conversion Diff',
            'type': 'general',
            'code': 'DIFF0123456789',
            'currency_id': cls.currency_usd.id,
            'payment_credit_account_id': cls.account_711.id,
            'payment_debit_account_id': cls.account_811.id
        })
        cls.env.company.write({
            'currency_conversion_diff_journal_id': cls.conversion_diff_journal.id,
            'income_currency_conversion_diff_account_id': cls.account_711.id,
            'expense_currency_conversion_diff_account_id': cls.account_811.id
        })
        cls.account_payment_method_manual_in = cls.env.ref('account.account_payment_method_manual_in')
        cls.acquirer_paypal = cls.env.ref('payment.payment_acquirer_paypal')
        cls.acquirer_paypal.write({
            'journal_id': cls.bank_journal_usd.id
        })

        cls.product_A = cls.env['product.product'].create({
            'name': 'Product A'
        })
        cls.product_B = cls.env['product.product'].create({
            'name': 'Product B'
        })

    def test_01_currency_conversion_diff(self):
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 110,
            'wallet_amount': 110,
            'currency_id': self.currency_usd.id,
            'partner_country_id': self.country_us.id,
            'reference': 'WALLET',
            'state': 'done',
            'type': 'form'
        })
        payment = self.env['account.payment'].create({
            'amount': 99,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'currency_id': self.currency_eur.id,
            'payment_method_id': self.account_payment_method_manual_in.id,
            'journal_id': self.bank_journal_usd.id,
            'date': datetime.date(2020, 1, 1),
            'payment_transaction_id': transaction.id,
            'wallet': True
        })
        payment.action_post()
        receivable_lines = self.env['account.move.line'].search([('payment_id', '=', payment.id), ('account_id.internal_type', '=', 'receivable')])
        self.assertRecordValues(receivable_lines, [{
            'debit': 0,
            'credit': 1.1,
            'wallet': True,
            'wallet_amount': 1.1
        }, {
            'debit': 0,
            'credit': 108.9,
            'wallet': True,
            'wallet_amount': 108.9
        }])

    def test_02_currency_conversion_diff(self):
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 110,
            'wallet_amount': 110,
            'currency_id': self.currency_usd.id,
            'partner_country_id': self.country_us.id,
            'reference': 'WALLET',
            'state': 'done',
            'type': 'form'
        })
        payment = self.env['account.payment'].create({
            'amount': 100,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'currency_id': self.currency_eur.id,
            'payment_method_id': self.account_payment_method_manual_in.id,
            'journal_id': self.bank_journal_usd.id,
            'date': datetime.date(2020, 1, 1),
            'payment_transaction_id': transaction.id,
            'wallet': True
        })
        payment.action_post()
        receivable_lines = self.env['account.move.line'].search([('payment_id', '=', payment.id), ('account_id.internal_type', '=', 'receivable')])
        self.assertRecordValues(receivable_lines, [{
            'debit': 0,
            'credit': 110,
            'wallet': True,
            'wallet_amount': 110
        }])

    def test_03_currency_conversion_diff(self):
        self.currency_vnd = self.env.ref('base.VND')
        self.currency_vnd.write({
            'rounding': 0.01
        })
        self.currency_vnd.rate_ids = self.env['res.currency.rate'].create({
            'name': datetime.date(2020, 1, 1),
            'currency_id': self.currency_vnd.id,
            'inverse_rate': 22856.5
        })
        self.currency_usd.rate_ids.write({
            'inverse_rate': 1
        })

        self.acquirer_paypal.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': self.currency_vnd.id,
                })
            ],
            'default_converted_currency_id': self.currency_vnd.id,
            'journal_id': self.bank_journal_vn.id
        })

        self.wallet = self.env['wallet'].create({
            'currency_id': self.currency_usd.id,
            'partner_id': self.partner.id
        })
        self.product = self.env['product.product'].create({
            'name': 'Product A'
        })
        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': datetime.date(2022, 4, 4),
            'currency_id': self.currency_usd.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 1,
                    'price_unit': 8688710,
                })
            ]
        })
        self.transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 9179895.0,
            'wallet_amount': 491185.0,
            'currency_id': self.currency_usd.id,
            'partner_country_id': self.country_us.id,
            'partner_id': self.partner.id,
            'reference': 'S00001-1',
            'state': 'done',
            'type': 'form',
            'wallet_id': self.wallet.id,
            'converted_currency_id': self.currency_vnd.id,
            'date': datetime.datetime(2020, 1, 1, 0, 0, 0),
            'invoice_ids': [(4, self.invoice.id)]
        })
        self.transaction._create_payment()

        self.assertEqual(self.wallet.amount, 491185.0)
        self.assertEqual(self.invoice.payment_state, 'paid')

    def test_04_currency_conversion_diff_loss(self):
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 110,
            'wallet_amount': 110,
            'currency_id': self.currency_usd.id,
            'partner_country_id': self.country_us.id,
            'reference': 'WALLET',
            'state': 'done',
            'type': 'form'
        })
        payment = self.env['account.payment'].create({
            'amount': 99,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'currency_id': self.currency_eur.id,
            'payment_method_id': self.account_payment_method_manual_in.id,
            'journal_id': self.bank_journal_usd.id,
            'date': datetime.date(2020, 1, 1),
            'payment_transaction_id': transaction.id,
            'wallet': True
        })
        payment.action_post()
        conversion_diff_move = self.env['account.move'].search([('payment_id', '=', payment.id),
                                                                ('journal_id', '=', self.conversion_diff_journal.id)],
                                                                limit=1)
        self.assertRecordValues(conversion_diff_move.line_ids, [{
            'debit': 0,
            'credit': 1.1,
            'account_id': self.partner.commercial_partner_id.property_account_receivable_id.id,
            'wallet': True,
            'wallet_amount': 1.1,
            'wallet_amount_currency': 1
        }, {
            'debit': 1.1,
            'credit': 0,
            'account_id': self.account_811.id,
            'wallet': True,
            'wallet_amount': -1.1,
            'wallet_amount_currency': -1
        }])

    def test_05_currency_conversion_diff_gain(self):
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 110,
            'wallet_amount': 110,
            'currency_id': self.currency_usd.id,
            'partner_country_id': self.country_us.id,
            'reference': 'WALLET',
            'state': 'done',
            'type': 'form'
        })
        payment = self.env['account.payment'].create({
            'amount': 101,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'currency_id': self.currency_eur.id,
            'payment_method_id': self.account_payment_method_manual_in.id,
            'journal_id': self.bank_journal_usd.id,
            'date': datetime.date(2020, 1, 1),
            'payment_transaction_id': transaction.id,
            'wallet': True
        })
        payment.action_post()
        conversion_diff_move = self.env['account.move'].search([('payment_id', '=', payment.id),
                                                                ('journal_id', '=', self.conversion_diff_journal.id)],
                                                                limit=1)
        self.assertRecordValues(conversion_diff_move.line_ids, [{
            'debit': 1.1,
            'credit': 0,
            'account_id': self.partner.commercial_partner_id.property_account_receivable_id.id,
            'wallet': True,
            'wallet_amount': -1.1,
            'wallet_amount_currency': -1
        }, {
            'debit': 0,
            'credit': 1.1,
            'account_id': self.account_711.id,
            'wallet': True,
            'wallet_amount': 1.1,
            'wallet_amount_currency': 1
        }])

    def test_06_currency_conversion_diff_loss_vnd_usd_only_app(self):
        self.cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", [self.currency_vnd.id, self.env.company.id])
        self.env['res.currency.rate'].search([]).unlink()
        currency_rate_vals = [
            {
                'name': '2022-01-01',
                'rate': 1,
                'currency_id': self.currency_vnd.id
            },
            {
                'name': '2022-01-01',
                'inverse_rate': 21000,
                'currency_id': self.currency_usd.id
            },
        ]
        self.env['res.currency.rate'].create(currency_rate_vals)

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': datetime.date(2022, 4, 4),
            'currency_id': self.currency_vnd.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product_A.id,
                    'quantity': 1,
                    'price_unit': 1215980,
                })
            ]
        })
        invoice._post(soft=False)
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 1215980,
            'wallet_amount': 0,
            'currency_id': self.currency_vnd.id,
            'partner_country_id': self.country_vn.id,
            'partner_id': self.partner.id,
            'reference': 'S00001-1',
            'state': 'done',
            'type': 'form',
            'converted_currency_id': self.currency_usd.id,
            'date': datetime.datetime(2022, 4, 4, 0, 0, 0),
            'invoice_ids': [(4, invoice.id)]
        })
        payment = transaction._create_payment()
        conversion_diff_move = self.env['account.move'].search([('payment_id', '=', payment.id),
                                                                ('journal_id', '=', self.conversion_diff_journal.id)],
                                                                limit=1)
        self.assertRecordValues(conversion_diff_move.line_ids, [{
            'debit': 0,
            'credit': 80,
            'account_id': self.partner.commercial_partner_id.property_account_receivable_id.id,
            'wallet': False,
        }, {
            'debit': 80,
            'credit': 0,
            'account_id': self.account_811.id,
            'wallet': False,
        }])
        self.assertEqual(invoice.payment_state, 'paid')

    def test_08_currency_conversion_diff_loss_usd_vnd_only_app(self):
        self.cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", [self.currency_vnd.id, self.env.company.id])
        self.env['res.currency.rate'].search([]).unlink()
        currency_rate_vals = [
            {
                'name': '2022-01-01',
                'rate': 1,
                'currency_id': self.currency_vnd.id
            },
            {
                'name': '2022-01-01',
                'inverse_rate': 21000,
                'currency_id': self.currency_usd.id
            },
        ]
        self.env['res.currency.rate'].create(currency_rate_vals)

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': datetime.date(2022, 4, 4),
            'currency_id': self.currency_usd.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product_A.id,
                    'quantity': 1,
                    'price_unit': 69.5,
                    'wallet': False,
                })
            ]
        })
        invoice._post(soft=False)
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 69.5,
            'wallet_amount': 0,
            'currency_id': self.currency_usd.id,
            'partner_country_id': self.country_vn.id,
            'partner_id': self.partner.id,
            'reference': 'S00001-1',
            'state': 'done',
            'type': 'form',
            'converted_currency_id': self.currency_vnd.id,
            'date': datetime.datetime(2022, 4, 4, 0, 0, 0),
            'invoice_ids': [(4, invoice.id)]
        })
        payment = transaction._create_payment()
        conversion_diff_move = self.env['account.move'].search([('payment_id', '=', payment.id),
                                                                ('journal_id', '=', self.conversion_diff_journal.id)],
                                                                limit=1)
        self.assertFalse(conversion_diff_move)
        self.assertEqual(invoice.payment_state, 'paid')

    def test_09_currency_conversion_diff_loss_usd_vnd_app_and_saas(self):
        self.cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", [self.currency_vnd.id, self.env.company.id])
        self.env['res.currency.rate'].search([]).unlink()
        currency_rate_vals = [
            {
                'name': '2022-01-01',
                'rate': 1,
                'currency_id': self.currency_vnd.id
            },
            {
                'name': '2022-01-01',
                'inverse_rate': 21000,
                'currency_id': self.currency_usd.id
            },
        ]
        self.env['res.currency.rate'].create(currency_rate_vals)

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': datetime.date(2022, 4, 4),
            'currency_id': self.currency_usd.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product_A.id,
                    'quantity': 1,
                    'price_unit': 69.5,
                    'wallet': False,
                }),
                (0, 0, {
                    'product_id': self.product_B.id,
                    'quantity': 1,
                    'price_unit': 33.5,
                    'wallet': False,
                })
            ]
        })
        invoice._post(soft=False)
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 103,
            'wallet_amount': 0,
            'currency_id': self.currency_usd.id,
            'partner_country_id': self.country_vn.id,
            'partner_id': self.partner.id,
            'reference': 'S00001-1',
            'state': 'done',
            'type': 'form',
            'converted_currency_id': self.currency_vnd.id,
            'date': datetime.datetime(2022, 4, 4, 0, 0, 0),
            'invoice_ids': [(4, invoice.id)]
        })
        payment = transaction._create_payment()
        conversion_diff_move = self.env['account.move'].search([('payment_id', '=', payment.id),
                                                                ('journal_id', '=', self.conversion_diff_journal.id)],
                                                                limit=1)
        self.assertFalse(conversion_diff_move)
        self.assertEqual(invoice.payment_state, 'paid')

    def test_10_currency_conversion_diff_gain_vnd_usd_only_app(self):
        self.cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", [self.currency_vnd.id, self.env.company.id])
        self.env['res.currency.rate'].search([]).unlink()
        currency_rate_vals = [
            {
                'name': '2022-01-01',
                'rate': 1,
                'currency_id': self.currency_vnd.id
            },
            {
                'name': '2022-01-01',
                'inverse_rate': 21000,
                'currency_id': self.currency_usd.id
            },
        ]
        self.env['res.currency.rate'].create(currency_rate_vals)

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': datetime.date(2022, 4, 4),
            'currency_id': self.currency_vnd.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product_A.id,
                    'quantity': 1,
                    'price_unit': 1315980,
                })
            ]
        })
        invoice._post(soft=False)
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 1315980,
            'wallet_amount': 0,
            'currency_id': self.currency_vnd.id,
            'partner_country_id': self.country_vn.id,
            'partner_id': self.partner.id,
            'reference': 'S00001-1',
            'state': 'done',
            'type': 'form',
            'converted_currency_id': self.currency_usd.id,
            'date': datetime.datetime(2022, 4, 4, 0, 0, 0),
            'invoice_ids': [(4, invoice.id)]
        })
        payment = transaction._create_payment()
        conversion_diff_move = self.env['account.move'].search([('payment_id', '=', payment.id),
                                                                ('journal_id', '=', self.conversion_diff_journal.id)],
                                                                limit=1)
        self.assertRecordValues(conversion_diff_move.line_ids, [{
            'debit': 90,
            'credit': 0,
            'account_id': self.partner.commercial_partner_id.property_account_receivable_id.id,
            'wallet': False,
        }, {
            'debit': 0,
            'credit': 90,
            'account_id': self.account_711.id,
            'wallet': False,
        }])
        self.assertEqual(invoice.payment_state, 'paid')

    def test_11_currency_conversion_diff_gain_vnd_usd_app_and_saas(self):
        self.cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", [self.currency_vnd.id, self.env.company.id])
        self.env['res.currency.rate'].search([]).unlink()
        currency_rate_vals = [
            {
                'name': '2022-01-01',
                'rate': 1,
                'currency_id': self.currency_vnd.id
            },
            {
                'name': '2022-01-01',
                'inverse_rate': 21000,
                'currency_id': self.currency_usd.id
            },
        ]
        self.env['res.currency.rate'].create(currency_rate_vals)

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': datetime.date(2022, 4, 4),
            'currency_id': self.currency_vnd.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.product_A.id,
                    'quantity': 1,
                    'price_unit': 1315980,
                    'wallet': False,
                }),
                (0, 0, {
                    'product_id': self.product_B.id,
                    'quantity': 1,
                    'price_unit': 315490,
                    'wallet': True,
                })
            ]
        })
        invoice._post(soft=False)
        transaction = self.env['payment.transaction'].create({
            'acquirer_id': self.acquirer_paypal.id,
            'amount': 1631470,
            'wallet_amount': 315490,
            'currency_id': self.currency_vnd.id,
            'partner_country_id': self.country_vn.id,
            'partner_id': self.partner.id,
            'reference': 'S00001-1',
            'state': 'done',
            'type': 'form',
            'converted_currency_id': self.currency_usd.id,
            'date': datetime.datetime(2022, 4, 4, 0, 0, 0),
            'invoice_ids': [(4, invoice.id)]
        })
        payment = transaction._create_payment()
        conversion_diff_move = self.env['account.move'].search([('payment_id', '=', payment.id),
                                                                ('journal_id', '=', self.conversion_diff_journal.id)],
                                                                limit=1)
        self.assertRecordValues(conversion_diff_move.line_ids, [{
            'debit': 20,
            'credit': 0,
            'account_id': self.partner.commercial_partner_id.property_account_receivable_id.id,
            'wallet': True,
        }, {
            'debit': 0,
            'credit': 20,
            'account_id': self.account_711.id,
            'wallet': True,
        }])
        self.assertEqual(invoice.payment_state, 'paid')
