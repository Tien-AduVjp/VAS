from werkzeug import urls
from lxml import objectify

from odoo import fields
from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.exceptions import ValidationError

from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.addons.payment_nganluong.controllers.main import NganLuongController


class NganLuongCommon(PaymentAcquirerCommon):

    @classmethod
    def setUpClass(cls):
        super(NganLuongCommon, cls).setUpClass()

        cls.currency_vnd = cls.env.ref('base.VND')
        cls.currency_vnd.active = True
        cls.country_vn = cls.env['res.country'].search([('code', 'like', 'VN')], limit=1)

        state = cls.env['res.country.state'].create({
            'country_id': cls.country_belgium.id,
            'name': 'Antwerp',
            'code': 'ATW',
            })

        cls.buyer_values.update({
            'partner_state': state,
            'partner_state_id': state.id,
            'partner_state_name': state.name,
            'billing_partner_state': state,
            'billing_partner_state_id': state.id,
            'billing_partner_state_name': state.name,
            })

        cls.buyer.write({'state_id': state.id})

        cls.nganluong = cls.env.ref('payment_nganluong.payment_acquirer_nganluong')
        cls.nganluong.write({
            'nganluong_merchant_site_code': '48759',
            'nganluong_merchant_password': '12457899',
            'nganluong_receiver_email': 'test_receiver@mail.com',
            'state': 'test',
            })

@tagged('external', '-standard', 'post_install', '-at_install')
class NganLuongTest(NganLuongCommon):
    def test_10_form_render(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        # be sure not to do stupid things
        self.assertEqual(self.nganluong.state, 'test', 'test without test environment')

        # ----------------------------------------
        # Test: button direct rendering
        # ----------------------------------------
        # render the button

        res = self.nganluong.render(
            'test-ref0', 90000, self.currency_vnd.id,
            values=self.buyer_values)

        form_values = {
            'merchant_site_code': '48759',
            'return_url': urls.url_join(base_url, NganLuongController._return_url),
            'receiver': 'test_receiver@mail.com',
            'transaction_info': 'test-ref0',
            'order_code': 'test',
            'price': '90000.0',
            'discount': None,
            'currency': 'vnd',
            'quantity': '1',
            'tax': None,
            'fee_shipping': None,
            'fee_cal': None,
            'order_description': 'odoo',
            'buyer_info': '%s *|* %s *|* %s *|* %s' % (
                self.buyer_values.get('billing_partner_name'),
                self.buyer_values.get('billing_partner_email'),
                self.buyer_values.get('billing_partner_phone'),
                '%s, %s, %s, %s' % (
                    self.buyer_values.get('partner_address'),
                    self.buyer_values.get('partner_city'),
                    self.buyer_values.get('partner_state').name,
                    self.buyer_values.get('partner_country').name
                    )
                ),
            'affiliate_code': 'odoo',
            'acquirer_id': str(self.nganluong.id),
            'lang': 'en',
            'cancel_url': urls.url_join(base_url, NganLuongController._cancel_url),
            'notify_url': urls.url_join(base_url, NganLuongController._notify_url),
        }

        # check form result
        tree = objectify.fromstring(res)

        data_set = tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set), 1, 'NganLuong: Found %d "data_set" input instead of 1' % len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'), '/payment/nganluong/standard', 'NganLuong: wrong form POST url')
        for form_input in tree.input:
            if form_input.get('name') in ['submit', 'data_set']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values.get(form_input.get('name')),
                'NganLuong: wrong value for input %s: received %s instead of %s' % (form_input.get('name'), form_input.get('value'), form_values[form_input.get('name')])
            )

    def test_11_form_with_fees(self):
        # be sure not to do stupid things
        self.assertEqual(self.nganluong.state, 'test', 'test without test environment')

        # update acquirer: compute fees
        self.nganluong.write({
            'fees_active': True,
            'fees_dom_fixed': 1000.0,
            'fees_dom_var': 1.0,
            'fees_int_fixed': 1000.0,
            'fees_int_var': 1.0,
        })

        # remove amount,currency to avoid uncontrollable value
        self.buyer_values.pop('amount')
        self.buyer_values.pop('currency_id')

        # render the button
        res = self.nganluong.render(
            'test-ref0', 195000, self.currency_vnd.id,
            values=self.buyer_values)

        # check form result
        tree = objectify.fromstring(res)

        data_set = tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set), 1, 'NganLuong: Found %d "data_set" input instead of 1' % len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'), '/payment/nganluong/standard', 'NganLuong: wrong form POST url')
        for form_input in tree.input:
            if form_input.get('name') in ['fee_shipping']:
                self.assertEqual(form_input.get('value'), '2960.0', 'NganLuong: wrong computed fees')

    @mute_logger('odoo.addons.payment_nganluong.models.payment', 'ValidationError')
    def test_12_nganluong_form_management(self):
        # be sure not to do stupid things
        self.assertEqual(self.nganluong.state, 'test', 'test without test environment')

        # typical data posted by nganluong after client has successfully paid
        nganluong_post_data = {
            'transaction_info': 'test-ref0',
            'order_code': u'test-ref0',
            'price': u'195000.00',
            'payment_type': u'2',
            'token_nl': u'08D73520KX778924N',
            'payment_id': '123',
        }

        # should raise error about unknown tx
        with self.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(nganluong_post_data, 'nganluong')

        # create tx
        tx = self.env['payment.transaction'].create({
            'amount': 195000,
            'acquirer_id': self.nganluong.id,
            'acquirer_reference': 'test-ref0',
            'currency_id': self.currency_vnd.id,
            'reference': 'test-ref0',
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.country_vn.id})

        # validate it
        tx.form_feedback(nganluong_post_data, 'nganluong')
        # check
        self.assertEqual(tx.state, 'pending', 'NganLuong: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test-ref0', 'NganLuong: wrong txn_id after receiving a valid pending notification')

        # update tx
        tx.write({
            'state': 'draft',
            'acquirer_reference': False})

        # Accept detained payment
        self.nganluong.nganluong_accept_detained_payment = True

        # validate it
        tx.form_feedback(nganluong_post_data, 'nganluong')
        # check
        self.assertEqual(tx.state, 'done', 'NganLuong: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test-ref0', 'NganLuong: wrong txn_id after receiving a valid pending notification')

    def test_13_currency_no_support(self):
        self.assertEqual(self.nganluong.state, 'test', 'test without test environment')

        currency_eur = self.env.ref('base.EUR')
        self.nganluong.default_converted_currency_id = self.currency_vnd

        # remove amount,currency to avoid uncontrollable value
        self.buyer_values.pop('amount')
        self.buyer_values.pop('currency_id')

        today = fields.Date.today()
        converted_amount = currency_eur._convert(
            100,
            self.currency_vnd,
            self.nganluong.company_id,
            today)
        # create tx
        tx = self.env['payment.transaction'].create({
            'amount': 100,
            'converted_amount': converted_amount,
            'acquirer_id': self.nganluong.id,
            'acquirer_reference': 'test-ref1',
            'currency_id': currency_eur.id,
            'reference': 'test-ref1',
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.country_vn.id,
            'date': today
            })

        # render the button
        res = self.nganluong.render(
            'test-ref1', 100, currency_eur.id,
            values=self.buyer_values)

        # check form result
        tree = objectify.fromstring(res)
        for form_input in tree.input:
            if form_input.get('name') in ['price']:
                self.assertEqual(float(form_input.get('value', 0)), tx.converted_amount, 'NganLuong: wrong computed fees')

        # typical data posted by nganluong after client has successfully paid
        nganluong_post_data = {
            'transaction_info': 'test-ref1',
            'order_code': u'test-ref1',
            'price': converted_amount,
            'payment_type': u'2',
            'token_nl': u'08D73520KX778924N',
            'payment_id': '123',
        }
        tx.form_feedback(nganluong_post_data, 'nganluong')

        self.assertEqual(tx.state, 'pending', 'NganLuong: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test-ref1', 'NganLuong: wrong txn_id after receiving a valid pending notification')

        # Accept detained payment
        self.nganluong.nganluong_accept_detained_payment = True

        # validate it
        tx.form_feedback(nganluong_post_data, 'nganluong')
        # check
        self.assertEqual(tx.state, 'done', 'NganLuong: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test-ref1', 'NganLuong: wrong txn_id after receiving a valid pending notification')
