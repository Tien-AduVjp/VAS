from unittest.mock import patch

from odoo.tests import SavepointCase, tagged
from odoo.exceptions import ValidationError, AccessError
from odoo import fields


@tagged('post_install', '-at_install')
class TestAccountPayment(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(SavepointCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True, no_reset_password=True))
        cls.currency_usd = cls.env.ref('base.USD')
        cls.partner = cls.env['res.partner'].create({
            'name': 'Ngoc'
        })
        cls.account_other_income = cls.env['account.account'].create({
            'name': 'Other Income',
            'code': 7110001,
            'user_type_id': cls.env.ref('account.data_account_type_other_income').id
        })
        cls.account_other_expenses = cls.env['account.account'].create({
            'name': 'Other Expenses',
            'code': 8110001,
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id
        })
        cls.bank_journal_usd = cls.env['account.journal'].create({
            'name': 'Bank USD',
            'type': 'bank',
            'code': 'BNK0123456789',
            'currency_id': cls.currency_usd.id
        })
        cls.account_payment_method_manual_in = cls.env.ref('account.account_payment_method_manual_in')
        cls.user_accountant = cls.env['res.users'].create({
            'name': 'user_accountant',
            'login': 'user_accountant@example.viindoo.com',
            'email': 'user_accountant@example.viindoo.com',
            'groups_id': [(6, 0, cls.env.ref('account.group_account_user').ids)],
        })
        cls.user_account_admin = cls.env['res.users'].create({
            'name': 'user_account_admin',
            'login': 'user_account_admin@example.viindoo.com',
            'email': 'user_account_admin@example.viindoo.com',
            'groups_id': [(6, 0, cls.env.ref('account.group_account_manager').ids)],
        })
        cls.env['account.payment'].create({
            'amount': 1000000,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': cls.partner.id,
            'payment_method_id': cls.account_payment_method_manual_in.id,
            'journal_id': cls.bank_journal_usd.id,
            'wallet': True
        }).action_post()
        cls.wallet = cls.partner.commercial_partner_id.wallet_ids

    def test_adjust_wallet_amount(self):
        wallet = self.wallet
        self.assertEqual(wallet.amount, 1000000)

        wizard = self.env['wallet.adjust'].create({
            'wallet_id': wallet.id,
            'amount': 500000,
            'account_id': self.account_other_income.id
        })
        wizard.action_adjust()
        self.assertEqual(wallet.adjustment_move_ids.wallet_total, 500000)
        self.assertRecordValues(wallet.adjustment_move_ids.line_ids, [{
            'account_id': self.account_other_income.id,
            'partner_id': self.partner.id,
            'debit': 500000,
            'credit': 0,
            'currency_id': self.currency_usd.id,
            'amount_currency': 500000,
            'wallet': False,
            'wallet_id': False,
            'wallet_amount': 0,
            'wallet_amount_currency': 0,
            'is_wallet_adjustment': False
        },
            {
            'account_id': self.partner.commercial_partner_id.property_account_receivable_id.id,
            'partner_id': self.partner.id,
            'debit': 0,
            'credit': 500000,
            'currency_id': self.currency_usd.id,
            'amount_currency': -500000,
            'wallet': True,
            'wallet_id': wallet.id,
            'wallet_amount': 500000,
            'wallet_amount_currency': 500000,
            'is_wallet_adjustment': True
        }])
        self.assertEqual(wallet.amount, 1500000)

        wizard = self.env['wallet.adjust'].create({
            'wallet_id': wallet.id,
            'amount':-200000,
            'account_id': self.account_other_expenses.id
        })
        wizard.action_adjust()
        self.assertEqual(wallet.adjustment_move_ids[0].wallet_total, -200000)
        self.assertEqual(wallet.amount, 1300000)
        self.assertRecordValues(wallet.adjustment_move_ids[0].line_ids[1], [{
            'account_id': self.partner.commercial_partner_id.property_account_receivable_id.id,
            'partner_id': self.partner.id,
            'debit':  200000,
            'credit': 0,
            'currency_id': self.currency_usd.id,
            'amount_currency': 200000,
            'wallet': True,
            'wallet_id': wallet.id,
            'wallet_amount': -200000,
            'wallet_amount_currency': -200000,
            'is_wallet_adjustment': True
        }])

    def test_raise_error_when_adjust_wallet_3(self):
        wallet = self.wallet
        with self.assertRaises(ValidationError, msg="adjust amount equal to 0"):
            self.env['wallet.adjust'].create({
                'wallet_id': wallet.id,
                'amount': 0,
                'account_id': self.account_other_income.id
            }).action_adjust()

    @patch.object(fields.Date, 'context_today', lambda *arg, **kwarg: fields.Date.to_date('2021-10-7'))
    def test_force_adjustment_Date(self):
        wallet = self.wallet
        self.env['wallet.adjust'].create({
            'wallet_id': wallet.id,
            'account_id': self.account_other_income.id,
            'amount': 500000}).action_adjust()
        self.assertEqual(wallet.adjustment_move_ids.date, fields.Date.to_date('2021-10-7'))
        self.env['wallet.adjust'].create({
            'wallet_id': wallet.id,
            'amount': 500000,
            'date': fields.Date.to_date('2021-10-1'),
            'account_id': self.account_other_income.id
        }).action_adjust()
        self.assertEqual(wallet.adjustment_move_ids[1].date, fields.Date.to_date('2021-10-1'))

    def test_access_rights(self):
        wallet = self.wallet
        with self.assertRaises(AccessError):
            self.env['wallet.adjust'].with_user(self.user_accountant).create({
                'wallet_id': wallet.id,
                'amount': 500000,
                'account_id': self.account_other_income.id
            }).action_adjust()
        self.env['wallet.adjust'].with_user(self.user_account_admin).create({
            'wallet_id': wallet.id,
            'amount': 500000,
            'account_id': self.account_other_income.id
        }).action_adjust()
