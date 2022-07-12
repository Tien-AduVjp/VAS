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

        Rate = cls.env['res.currency.rate']
        cls.currency_usd.rate_ids = Rate.create({
            'name': datetime.date(2020, 1, 1),
            'rate': 1.1
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Ngoc'
        })
        cls.country_us = cls.env.ref('base.us')

        cls.bank_journal_usd = cls.env['account.journal'].create({
            'name': 'Bank USD',
            'type': 'bank',
            'code': 'BNK0123456789',
            'currency_id': cls.currency_usd.id
        })

        cls.account_711 = cls.env['account.account'].create({
            'name': 'Thu nhap khac',
            'code': 711001,
            'user_type_id': cls.env.ref('account.data_account_type_other_income').id,
            'currency_id': cls.currency_usd.id
        })
        cls.account_811 = cls.env['account.account'].create({
            'name': 'Chi phi khac',
            'code': 811001,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
            'currency_id': cls.currency_usd.id
        })
        cls.conversion_diff_journal = cls.env['account.journal'].create({
            'name': 'Conversion Diff',
            'type': 'general',
            'code': 'DIFF0123456789',
            'currency_id': cls.currency_usd.id,
            'default_credit_account_id': cls.account_711.id,
            'default_debit_account_id': cls.account_811.id
        })
        cls.env.company.currency_conversion_diff_journal_id = cls.conversion_diff_journal
        cls.account_payment_method_manual_in = cls.env.ref('account.account_payment_method_manual_in')
        cls.acquirer_paypal = cls.env.ref('payment.payment_acquirer_paypal')

    def test_currency_conversion_diff(self):
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
            'payment_date': datetime.date(2020, 1, 1),
            'payment_transaction_id': transaction.id,
            'wallet': True
        })
        payment.post()
        receivable_lines = payment.move_line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable').sorted(key='id')
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
    
    def test_currency_conversion_diff_2(self):
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
            'payment_date': datetime.date(2020, 1, 1),
            'payment_transaction_id': transaction.id,
            'wallet': True
        })
        payment.post()
        receivable_lines = payment.move_line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable').sorted(key='id')
        self.assertRecordValues(receivable_lines, [{
            'debit': 0,
            'credit': 110,
            'wallet': True,
            'wallet_amount': 110
        }])
