import datetime

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase, Form, tagged
from odoo.tools import mute_logger
from odoo.addons.to_wallet.tests.test_common import TestWalletCommon


@tagged('post_install', '-at_install')
class TestSaleWallet(TestWalletCommon):
    
    @classmethod
    def setUpClass(cls):
        super(TestSaleWallet, cls).setUpClass()
        
        cls.wallet_product = cls.env['product.product'].create({
            'name': 'Wallet Product',
            'type': 'service',
            'wallet': True
        })
        cls.pricelist_usd = cls.env['product.pricelist'].create({
            'name': 'USD pricelist',
            'active': True,
            'currency_id': cls.currency_usd.id,
            'company_id': cls.env.company.id,
        })
        cls.pricelist_eur = cls.env['product.pricelist'].create({
            'name': 'EUR pricelist',
            'active': True,
            'currency_id': cls.currency_eur.id,
            'company_id': cls.env.company.id,
        })
    
    @classmethod
    def create_sale_order(cls, custom_vals={}, custom_line_vals_list=[], confirm=True):
        line_vals_list = []
        for custom_line_vals in custom_line_vals_list:
            line_vals = {
                'product_id': cls.wallet_product.id,
                'name': cls.wallet_product.name,
                'price_unit': 0,
                'tax_id': [(5, 0, 0)],
            }
            line_vals.update(custom_line_vals)
            line_vals_list.append(line_vals)
        vals = {
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, vals) for vals in line_vals_list],
            'date_order': datetime.date(2020, 1, 1),
            'pricelist_id': cls.pricelist_usd.id
        }
        vals.update(custom_vals)
        order = cls.env['sale.order'].create(vals)
        if confirm:
            order.action_confirm()
        return order
    
    @classmethod
    @mute_logger('odoo.addons.payment.models.payment_acquirer')
    def create_payment_transaction(cls, order, post_process=True, custome_value={}):
        vals = {
            'acquirer_id': cls.acquirer_wire_transfer.id,
            'return_url': '/shop/payment/validate',
            'state': 'done',
        }
        vals.update(custome_value)
        transaction = order._create_payment_transaction(vals)
        transaction.render_sale_button(order)
        if post_process:
            transaction._post_process_after_done()
        return transaction
        
    def test_create_invoice_with_wallet_product(self):
        order = self.create_sale_order(custom_line_vals_list=[{
                'price_unit': 100000
            }])
        order._create_invoices()
        self.assertTrue(order.order_line.invoice_lines.wallet)
    
    def test_payment_online(self):
        order = self.create_sale_order(custom_line_vals_list=[{
                'price_unit': 100000
            }], confirm=False)
        transaction = self.create_payment_transaction(order)
        self.assertRecordValues(transaction, [{
            'reference': '%s-1' % order.name,
            'amount': 100000,
            'wallet_amount': 100000,
        }])
        self.assertRecordValues(transaction.payment_id, [{
            'amount': 100000,
            'wallet': True,
            'wallet_amount': 100000,
        }])
    
    def test_payment_online_2(self):
        order = self.create_sale_order(custom_line_vals_list=[{
                'price_unit': 100000
            },
            {   
                'product_id': self.product.id,
                'price_unit': 100000
            }], confirm=False)
        transaction = self.create_payment_transaction(order)
        self.assertRecordValues(transaction, [{
            'reference': '%s-1' % order.name,
            'amount': 200000,
            'wallet_amount': 100000,
        }])
        self.assertRecordValues(transaction.payment_id, [{
            'amount': 200000,
            'wallet': True,
            'wallet_amount': 100000,
        }])
    
    def test_payment_online_currency(self):
        order = self.create_sale_order(custom_vals={'pricelist_id': self.pricelist_eur.id}, custom_line_vals_list=[{
                'price_unit': 100
            }], confirm=False)
        transaction = self.create_payment_transaction(order)
        self.assertRecordValues(transaction.payment_id, [{
            'amount': 100,
            'wallet': True,
            'wallet_amount': 100,
            'currency_id': self.currency_eur.id
        }])
        self.assertRecordValues(self.partner.commercial_partner_id.wallet_ids, [
            {
                'currency_id': self.currency_eur.id,
                'amount': 100
            }
        ])
