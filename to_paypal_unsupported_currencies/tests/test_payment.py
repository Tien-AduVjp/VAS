import json
from lxml import html

from odoo import fields
from odoo.tests import tagged, SavepointCase
from odoo.tools.float_utils import float_compare

from odoo.addons.to_paypal_unsupported_currencies.models.payment_acquirer import PAYPAL_SUPPORTED_CURRENCIES


@tagged('post_install', '-at_install', 'external')
class TestPayment(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPayment, cls).setUpClass()

        cls.partner = cls.env['res.partner'].create({'name': 'partner'})

        cls.env.ref('base.rateUSDbis').write({
            'name': fields.Date.to_date('%s-01-01'%fields.Date.today().year)
        })
        cls.currency_eur = cls.env.ref('base.EUR')
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_vnd = cls.env.ref('base.VND')
        cls.currency_eur.active = True
        cls.currency_usd.active = True
        cls.currency_vnd.active = True

        cls.paypal = cls.env.ref('payment.payment_acquirer_paypal')
        cls.paypal.write({
            'paypal_email_account': 'dummy',
            'state': 'test',
        })

        # Setup default converted currency for paypal
        cls.paypal.write({
            'default_converted_currency_id': cls.currency_usd.id
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product A',
        })

        cls.env.company.partner_id.write({'country_id': cls.env.ref('base.us').id})

    def test_after_install_module_01(self):
        """
        [Functional Test] - TC01

        - Case: Check supported currency map of paypal after install module
        - Expected Result: paypal will have supported currency map as configuration in PAYPAL_SUPPORTED_CURRENCIES
        """
        supported_currencies = self.paypal.supported_currency_map_ids.currency_id.mapped('name')
        self.assertTrue(len(supported_currencies) == len(PAYPAL_SUPPORTED_CURRENCIES))
        self.assertTrue(set(supported_currencies) == set(PAYPAL_SUPPORTED_CURRENCIES))

    def test_payment_render_01(self):
        """
        [Functional Test] - TC02

        - Case: Render payment in case:
            + invoice has currency is VND
            + VND is not in supported currencies of pyapal
            + default converted currency of paypal is USD
        - Expected Result:
            + currency on payment form is USD
            + amount on payment form is converted to USD
            + there are custom information of unsupported currency in payment form
        """

        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'invoice_date': fields.Date.from_string('2021-08-27'),
                'currency_id': self.currency_vnd.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 30,
                        'price_unit': 100000,
                    })
                ]
            })

        invoice.action_post()

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.paypal.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        res = self.paypal.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        tree = html.fromstring(res)

        currency_code = tree.xpath("//input[@name='currency_code']")[0].value
        amount = float(tree.xpath("//input[@name='amount']")[0].value)
        custom_values = json.loads(tree.xpath("//input[@name='custom']")[0].value)
        unsupported_currency_code = custom_values.get('unsupported_currency_code', False)
        unsupported_currency_amount = custom_values.get('unsupported_currency_amount', False)
        self.assertTrue(currency_code == 'USD')
        self.assertTrue(float_compare(amount, 174.20, 2) == 0)
        self.assertTrue(unsupported_currency_code == 'VND')
        self.assertTrue(float_compare(unsupported_currency_amount, 3000000.0, 2) == 0)

        # typical data posted by paypal after client has successfully paid to test _paypal_form_get_invalid_parameters
        transaction_ref = transaction.reference
        paypal_post_data = {
            'protection_eligibility': u'Ineligible',
            'last_name': u'Test',
            'txn_id': u'08D73520KX778924N',
            'receiver_email': 'dummy',
            'payment_status': u'Pending',
            'payment_gross': u'',
            'tax': u'0.00',
            'residence_country': u'FR',
            'address_state': u'Alsace',
            'payer_status': u'verified',
            'txn_type': u'web_accept',
            'address_street': u'Av. de la Pelouse, 87648672 Mayet',
            'handling_amount': u'0.00',
            'payment_date': u'03:21:19 Aug 30, 2021 PST',
            'first_name': u'Norbert',
            'item_name': transaction_ref,
            'address_country': u'France',
            'charset': u'windows-1252',
            'custom': u'{"return_url": "/payment/process", "unsupported_currency_code":"VND", "unsupported_currency_amount": 3000000.0}',
            'notify_version': u'3.7',
            'address_name': u'Norbert Poilu',
            'pending_reason': u'multi_currency',
            'item_number': transaction_ref,
            'receiver_id': self.paypal.paypal_seller_account,
            'transaction_subject': u'',
            'business': u'dummy',
            'test_ipn': u'1',
            'payer_id': u'VTDKRZQSAHYPS',
            'verify_sign': u'An5ns1Kso7MWUdW4ErQKJJJ4qi4-AVoiUf-3478q3vrSmqh08IouiYpM',
            'address_zip': u'75002',
            'address_country_code': u'FR',
            'address_city': u'Paris',
            'address_status': u'unconfirmed',
            'mc_currency': u'USD',
            'shipping': u'0.00',
            'payer_email': u'tde+buyer@odoo.com',
            'payment_type': u'instant',
            'mc_gross': u'174.2',
            'ipn_track_id': u'866df2ccd444b',
            'quantity': u'1'
        }
        # Expect run without error
        transaction.form_feedback(paypal_post_data, 'paypal')

    def test_payment_render_02(self):
        """
        [Functional Test] - TC03

        - Case: Render payment in case:
            + add VND to supported currencies of paypal
            + invoice has currency is VND
            + default converted currency of paypal is USD
        - Expected Result:
            + currency on payment form is VND
            + amount on payment form is not changed
        """

        self.paypal.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': self.currency_vnd.id,
                })
            ]
        })
        self.paypal.invalidate_cache()

        # Create invoice
        invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.partner.id,
                'invoice_date': fields.Date.from_string('2021-08-27'),
                'currency_id': self.currency_vnd.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': self.product.id,
                        'quantity': 3,
                        'price_unit': 100000,
                    })
                ]
            })

        # Create payment transaction from invoice
        transaction = invoice._create_payment_transaction({
            'acquirer_id': self.paypal.id,
        })

        # Render payment form and check data in payment transaction
        values = {
            'partner_id': invoice.partner_id.id,
            'type': transaction.type,
            'type': 'form',
        }
        res = self.paypal.with_context(submit_class='btn btn-primary', submit_txt='Pay & Confirm').sudo().render(
            transaction.reference,
            invoice.amount_residual,
            invoice.currency_id.id,
            values=values,
        )

        tree = html.fromstring(res)

        currency_code = tree.xpath("//input[@name='currency_code']")[0].value
        amount = float(tree.xpath("//input[@name='amount']")[0].value)
        custom_values = json.loads(tree.xpath("//input[@name='custom']")[0].value)
        unsupported_currency_code = custom_values.get('unsupported_currency_code', False)
        unsupported_currency_amount = custom_values.get('unsupported_currency_amount', False)
        self.assertTrue(currency_code == 'VND')
        self.assertTrue(float_compare(amount, 300000.0, 2) == 0)
        self.assertTrue(not unsupported_currency_code)
        self.assertTrue(not unsupported_currency_amount)
