from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestCurrencyRateInvoices(Common):
    
    """ Sales Invoice """
    def test_sales_invoice_rate_have_bank_default(self, type_invoice='out_invoice'):
        """ *Have bank default* """
        """ Get newest buy rate of bank default"""

        """ Case date invoice earlier all rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-01-01')
        self.assertEqual(journal_product.credit or journal_product.debit, 1)
    
        """ Case date invoice in day have 2 rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-05-05')
        self.assertEqual(journal_product.credit or journal_product.debit, 12000)
    
        """ Case date invoice later rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-08-08')
        self.assertEqual(journal_product.credit or journal_product.debit, 22000)
    
    def test_sales_invoice_rate_have_bank_default_but_no_have_rate(self, type_invoice='out_invoice'):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest buy rate ignore bank"""
        self.env.company.main_currency_bank_id = self.bank_no_rate
    
        """ Case date invoice in day have 2 rate"""
        _, journal_product = self.create_invoices('out_invoice', self.vnd, 1, '2021-05-05')
        self.assertEqual(journal_product.credit, 17000)
    
        """ Case date invoice later all rate"""
        _, journal_product = self.create_invoices('out_invoice', self.vnd, 1, '2021-08-08')
        self.assertEqual(journal_product.credit, 27000)
        
    def test_sales_invoice_rate_no_have_bank_default(self, type_invoice='out_invoice'):
        """ *Don't have bank default* """
        """ Get newest rate ignore type rate or bank """
        self.env.company.main_currency_bank_id = False

        """ Case date invoice in day have 2 rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-05-05')
        self.assertEqual(journal_product.credit or journal_product.debit, 18000)
        
        """ Case date invoice later all rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-08-08')
        self.assertEqual(journal_product.credit or journal_product.debit, 28000) 
        
    """ Refund Invoice """
    def test_refund_invoice_rate_have_bank_default(self):
        """ *Have bank default* """
        self.test_purchase_invoice_rate_have_bank_default(type_invoice='in_refund')
        
    def test_refund_invoice_rate_have_bank_default_but_no_have_rate(self):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest buy rate ignore bank"""
        self.test_sales_invoice_rate_have_bank_default_but_no_have_rate(type_invoice='in_refund')
        
    def test_refund_invoice_rate_no_have_bank_default(self):
        """ *Don't have bank default* """
        """ Get newest rate ignore type rate or bank """
        self.test_sales_invoice_rate_no_have_bank_default(type_invoice='in_refund')
        
    """ Purchase Invoice """
    def test_purchase_invoice_rate_have_bank_default(self, type_invoice='in_invoice'):
        """ *Have bank default* """
        """ Get newest sell rate of bank default"""

        """ Case date invoice in day have 2 rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-05-05')
        self.assertEqual(journal_product.debit or journal_product.credit, 10000)
    
        """ Case date invoice later rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-08-08')
        self.assertEqual(journal_product.debit or journal_product.credit, 20000)
        
    def test_purchase_invoice_rate_have_bank_default_but_no_have_rate(self, type_invoice='in_invoice'):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest sell rate ignore bank"""
        self.env.company.main_currency_bank_id = self.bank_no_rate
    
        """ Case date invoice in day have 2 rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-05-05')
        self.assertEqual(journal_product.debit, 15000)
    
        """ Case date invoice later all rate"""
        _, journal_product = self.create_invoices(type_invoice, self.vnd, 1, '2021-08-08')
        self.assertEqual(journal_product.debit, 25000)
        
    def test_purchase_invoice_rate_no_have_bank_default(self):
        """ *Don't have bank default* """
        """ Get newest rate ignore type rate or bank """
        self.test_sales_invoice_rate_no_have_bank_default(type_invoice='in_invoice')

    """ Credit Note Invoice """
    def test_credit_note_invoice_rate_have_bank_default(self):
        """ *Have bank default* """
        self.test_sales_invoice_rate_have_bank_default(type_invoice='out_refund')
        
    def test_credit_note_invoice_rate_have_bank_default_but_no_have_rate(self):
        """ *Have bank default but bank don't have any rate* """
        """ Get newest buy rate ignore bank"""
        self.test_sales_invoice_rate_have_bank_default_but_no_have_rate(type_invoice='out_refund')
        
    def test_credit_note_invoice_rate_no_have_bank_default(self):
        """ *Don't have bank default* """
        """ Get newest rate ignore type rate or bank """
        self.test_sales_invoice_rate_no_have_bank_default(type_invoice='out_refund')
