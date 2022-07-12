from odoo.tests import tagged, Form

from .common import Common


@tagged('post_install', '-at_install')
class TestCurrencyRatePayments(Common):

    @classmethod
    def setUpClass(cls):
        super(TestCurrencyRatePayments, cls).setUpClass()

        cls.bank_account_vnd = cls.env['res.partner.bank'].create({
            'acc_number': '2000',
            'partner_id': cls.env.company.id,
            'currency_id': cls.vnd.id
            })

        journal_bank_vnd_form = Form(cls.env['account.journal'].with_context(default_type='bank'))
        journal_bank_vnd_form.name = 'BankVND'
        journal_bank_vnd_form.code = 'BankVND'
        journal_bank_vnd_form.currency_id = cls.vnd
        journal_bank_vnd_form.bank_account_id = cls.bank_account_vnd
        cls.journal_bank_vnd = journal_bank_vnd_form.save()

    """ Not config bank on journal account """
    """ Payment send money """
    def test_rate_payment_send_money_have_bank_default(self):
        """ *Have bank default* """

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-05-05')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 10000)

        """ Case date invoice later date rate"""
        payment, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-08-08')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 20000)

        """ Try to change journal entry's date """
        journal_entry_form = Form(payment.move_id)
        journal_entry_form.date = '2021-06-06'
        journal_entry_form.save()
        self.assertEqual(journal_payment.debit or journal_payment.credit, 10000)

    def test_rate_payment_send_money_have_bank_default_but_no_have_rate(self):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest sell rate ignore bank"""
        self.env.company.main_currency_bank_id = self.bank_no_rate

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-05-05')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 15000)

        """ Case date invoice later all date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-08-08')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 25000)

    def test_rate_payment_send_money_no_have_bank_default(self):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest sell rate ignore bank"""
        self.env.company.main_currency_bank_id = False

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-05-05')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 18000)

        """ Case date invoice later all date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-08-08')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 28000)

    """ Payment receive money """
    def test_rate_payment_receive_monney_have_bank_default(self):
        """ Get newest buy rate of bank default"""

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-05-05' )
        self.assertEqual(journal_payment.debit or journal_payment.credit, 12000)

        """ Case date invoice later date rate"""
        payment, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-08-08' )
        self.assertEqual(journal_payment.debit or journal_payment.credit, 22000)

        """ Try to change journal entry's date """
        journal_entry_form = Form(payment.move_id)
        journal_entry_form.date = '2021-06-06'
        journal_entry_form.save()
        self.assertEqual(journal_payment.debit or journal_payment.credit, 12000)

    def test_rate_payment_receive_money_have_bank_default_but_no_have_rate(self):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest sell rate ignore bank"""
        self.env.company.main_currency_bank_id = self.bank_no_rate

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-05-05')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 17000)

        """ Case date invoice later all date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-08-08')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 27000)

    def test_rate_payment_receive_money_no_have_bank_default(self):
        """ *Don't have bank default* """
        """ Get newest rate ignore type rate or bank """
        self.env.company.main_currency_bank_id = False

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-05-05')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 18000)

        """ Case date invoice later all date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-08-08')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 28000)

    """ Payment internal transfer """
    """ Get sell rate if exchange from company currency to foreign currency and reverse get buy rate"""
    def test_rate_payment_internal_monney_have_bank_default(self):
        """ Get newest rate of bank default"""

        """ Case date invoice in day have 2 date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.debit, 12000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.credit, 10000)

        """ Case date invoice later date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.debit, 22000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.credit, 20000)

    def test_rate_payment_internal_money_have_bank_default_but_no_have_rate(self):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest rate ignore bank"""
        self.env.company.main_currency_bank_id = self.bank_no_rate

        """ Case date invoice in day have 2 date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.debit, 17000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.credit, 15000)

        """ Case date invoice later all date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.debit, 27000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.credit, 25000)

    def test_rate_payment_internal_money_no_have_bank_default(self):
        """ *Don't have bank default* """
        """ Get newest rate ignore type rate or bank """
        self.env.company.main_currency_bank_id = False

        """ Case date invoice in day have 2 date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.debit, 18000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.credit, 18000)

        """ Case date invoice later all date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.debit, 28000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.credit, 28000)

    """ Config bank on journal account """
    def test_rate_payment_send_config_bank_journal(self):
        self.default_journal_bank.bank_id = self.bank2

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-05-05')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 15000)

        """ Case date invoice later date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-08-08')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 25000)

    def test_rate_payment_send_config_bank_journal_but_no_rate(self):
        """ Get rate of bank default """
        self.default_journal_bank.bank_id = self.bank_no_rate

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-05-05')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 10000)

        """ Case date invoice later date rate"""
        _, journal_payment = self.create_payment('outbound', self.vnd, 1, date='2021-08-08')
        self.assertEqual(journal_payment.debit or journal_payment.credit, 20000)

    def test_rate_payment_receive_config_bank_journal(self):
        self.default_journal_bank.bank_id = self.bank2

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-05-05' )
        self.assertEqual(journal_payment.debit or journal_payment.credit, 17000)

        """ Case date invoice later date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-08-08' )
        self.assertEqual(journal_payment.debit or journal_payment.credit, 27000)

    def test_rate_payment_receive_config_bank_journal_but_no_rate(self):
        """ Get rate of bank default """
        self.default_journal_bank.bank_id = self.bank_no_rate

        """ Case date invoice in day have 2 date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-05-05' )
        self.assertEqual(journal_payment.debit or journal_payment.credit, 12000)

        """ Case date invoice later date rate"""
        _, journal_payment = self.create_payment('inbound', self.vnd, 1, date='2021-08-08' )
        self.assertEqual(journal_payment.debit or journal_payment.credit, 22000)

    def test_rate_payment_internal_config_bank_journal(self):
        """ Get rate of bank on source journal"""
        self.default_journal_bank.bank_id = self.bank2
        self.journal_bank_vnd.bank_id = self.bank_default

        """ Case date invoice in day have 2 date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.debit, 17000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-05-05')
        self.assertEqual(dest_journal_payment.credit, 15000)

        """ Case date invoice later all date rate"""
        _, dest_journal_payment = self.create_payment('outbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.debit, 27000)
        _, dest_journal_payment = self.create_payment('inbound', self.vnd, 1, internal_transfer=True, date='2021-08-08')
        self.assertEqual(dest_journal_payment.credit, 25000)
