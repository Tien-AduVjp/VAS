from lxml import html
import re

from odoo import http
from odoo.tests import tagged, HttpCase

from odoo.addons.website.tools import MockRequest


@tagged('post_install', '-at_install')
class TestWebsiteAffiliate(HttpCase):

    def setUp(self):
        super(TestWebsiteAffiliate, self).setUp()
        self.website = self.env['website'].browse(1)
        self.base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        self.user_portal = self.env.ref('base.demo_user0')
        self.user_admin = self.env.ref('base.user_admin')
        self.commission_rule_all = self.env['affiliate.commission.rule'].create({
            'name': '11%',
            'type': 'all',
            'affiliate_comm_percentage': 11.00,
        })
        self.product_1 = self.env['product.product'].create({
            'name': '123 Pro Max',
            'lst_price': 30000000,
            'categ_id': self.env.ref('product.product_category_all').id,
            'is_published': True
        })
        self.affiliate_code_admin = self.env['affiliate.code'].create({
            'partner_id': self.user_admin.partner_id.id
        })

    def test_website_affiliate_flow(self):
        # Case: access to /affiliate
        # Auto create affiliate code
        self.env.company.commission_product_id.write({
            'taxes_id': [(6, 0, [])],
            'supplier_taxes_id': [(6, 0, [])]
        })
        self.assertEqual(len(self.user_portal.affcode_ids), 0)
        with MockRequest(self.env, website=self.website, context={'lang': 'en_US'}):
            self.authenticate('portal', 'portal')
            self.url_open(self.base_url + '/affiliate')
        self.assertEqual(len(self.user_portal.affcode_ids), 1)
        self.logout()
        # User who joined the affiliate will not create any more affiliate code
        with MockRequest(self.env, website=self.website, context={'lang': 'en_US'}):
            self.authenticate('portal', 'portal')
            res = self.url_open(self.base_url + '/affiliate')
        self.assertEqual(len(self.user_portal.affcode_ids), 1)
        self.logout()
        # create link tracker with affiliate code
        with MockRequest(self.env, website=self.website, context={'lang': 'en_US'}):
            self.authenticate('portal', 'portal')
            resp = self.url_open(self.base_url + '/affiliate')
            root = html.fromstring(resp.content)
            data = {
                'csrf_token': root.xpath("//input[@name='csrf_token']")[0].value,
                'title': 'Title',
                'url': self.base_url + '/shop',
                'medium': self.env.ref('utm.utm_medium_website').id,
                'source': self.env.ref('utm.utm_source_facebook').id
            }
            self.url_open(self.base_url + '/affiliate/create_link', data=data)
            link_tracker = self.env['link.tracker'].search([('affiliate_code_id', '=', self.user_portal.affcode_ids.id)])
            self.assertTrue(link_tracker)
            self.logout()

        with MockRequest(self.env, website=self.website, context={'lang': 'en_US'}):
            # Case: Access link tracker => add to cart product => checkout
            # Result: A new quotation is generated with affiliate code
            self.opener.cookies['to_affiliate_param'] = self.user_portal.affcode_ids.name
            data = {
                'csrf_token': http.request.csrf_token(),
                'product_id': self.product_1.id
            }
            res = self.opener.post(self.base_url + '/shop/cart/update', data=data)
            order_id = int(html.fromstring(res.content).xpath("//sup")[0].attrib['data-order-id'])
            order = self.env['sale.order'].browse(order_id)
            res = self.url_open(self.base_url + '/shop/checkout?express=1')
            address_data = {'name': 'Lucas', 'email': 'lucass111@example.viindoo.com', 'phone': '123456789',
                            'company_name': 'My Company', 'vat': '', 'street': '23 Street 1', 'street2': '23 Street 2',
                            'zip': '', 'city': 'HP', 'country_id': '241', 'state_id': '1080', 'use_same': '1',
                            'csrf_token': html.fromstring(res.content).xpath("//input[@name='csrf_token']")[0].value,
                            'submitted': '1', 'partner_id': '-1', 'callback': '', 'field_required': 'phone,name'}
            self.opener.post(self.base_url + '/shop/address', data=address_data)
            self.assertEqual(self.user_portal.affcode_ids.sale_order_ids.state, 'draft')
            order.action_confirm()
            # Case: Confirm order
            # Result: A new commission is generated
            self.assertEqual(len(self.user_portal.get_affiliate_commissions()), 1)

            self.authenticate('portal', 'portal')
            res = self.url_open(self.base_url + '/affiliate/commissions')
            root = html.fromstring(res.content)
            commission_amount = root.xpath("//td[contains(@class, 'comission_amount')]/span")[0].text.split('.')[0]
            self.assertEqual(commission_amount, '3,300,000')

            # create payment request
            res = self.url_open(self.base_url + '/affiliate/payment_requests/new')
            root = html.fromstring(res.content)
            data = {
                'csrf_token': root.xpath("//input[@name='csrf_token']")[0].value,
                'notes': 'Payment request note test'
            }
            res = self.url_open(self.base_url + root.xpath("//form")[0].action, data=data)
            commission_total = html.fromstring(res.content).xpath("//div[contains(@class, 'payment_total')]/p/span")[0].text.split('.')[0]
            self.assertEqual(commission_total, '3,300,000')
            payment_request = self.env['affiliate.payment'].browse(int(res.url.split('/')[-1]))
            self.assertEqual(payment_request.state, 'confirm')

            # See invoice info
            # Case: No invoice
            # Result: Text = There are currently no affiliate invoices for your account.
            res = self.url_open(self.base_url + '/affiliate/invoices')
            content = html.fromstring(res.content).xpath("//div[@class='col-md-9 col-lg-8']//p")
            self.assertEqual(re.sub('(\t)|(\n)', '', content[0].text), 'There are currently no affiliate invoices for youraccount.')

            # Case: Unpaid invoice
            # Result: Invoice Status = There are currently no affiliate invoices for your account.
            payment_request.action_approve()
            payment_request.invoice_ids.action_post()
            res = self.url_open(self.base_url + '/affiliate/invoices')
            amount_due = html.fromstring(res.content).xpath(
                "//table[contains(@class, 'o_my_status_table')]/tr/td[5]//span[@class='oe_currency_value']")[0].text.split('.')[0]
            invoice_status = html.fromstring(res.content).xpath(
                "//table[contains(@class, 'o_my_status_table')]/tr/td[4]//i")[0].tail
            self.assertEqual(amount_due, '3,300,000')
            self.assertEqual(re.sub('(\t)|(\n)', '', invoice_status), 'Waiting for Payment')

            invoice = payment_request.invoice_ids
            journal_test = self.env['account.journal'].create({
                'name': 'Journal Test', 'type': 'bank', 'code': 'JournalTest',
                'currency_id': self.env.company.currency_id.id
            })
            # Case: Partial payment
            # Result: Invoice Status = Waiting for Payment.
            self.env['account.payment'].create({
                'payment_method_id': self.env.ref("account.account_payment_method_manual_out").id,
                'payment_type': 'outbound',
                'invoice_ids': [(6, 0, invoice.ids)],
                'amount': 300000,
                'journal_id': journal_test.id,
                'partner_type': 'customer',
            }).post()
            res = self.url_open(self.base_url + '/affiliate/invoices')
            invoice_status = html.fromstring(res.content).xpath(
                "//table[contains(@class, 'o_my_status_table')]/tr/td[4]//i")[0].tail
            amount_due = html.fromstring(res.content).xpath(
                "//table[contains(@class, 'o_my_status_table')]/tr/td[5]//span[@class='oe_currency_value']")[0].text.split('.')[0]
            self.assertEqual(amount_due, '3,000,000')
            self.assertEqual(re.sub('(\t)|(\n)', '', invoice_status), 'Waiting for Payment')

            # Case: Paid invoice
            # Result: Invoice Status = Paid. Amount Due = 0
            self.env['account.payment'].create({
                'payment_method_id': self.env.ref("account.account_payment_method_manual_out").id,
                'payment_type': 'outbound',
                'invoice_ids': [(6, 0, invoice.ids)],
                'amount': 30000000,
                'journal_id': journal_test.id,
                'partner_type': 'customer',
            }).post()
            res = self.url_open(self.base_url + '/affiliate/invoices')
            invoice_status = html.fromstring(res.content).xpath(
                "//table[contains(@class, 'o_my_status_table')]/tr/td[4]//i")[0].tail
            amount_due = html.fromstring(res.content).xpath(
                "//table[contains(@class, 'o_my_status_table')]/tr/td[5]//span[@class='oe_currency_value']")[0].text.split('.')[0]
            self.assertEqual(amount_due, '0')
            self.assertEqual(re.sub('(\t)|(\n)', '', invoice_status), 'Paid')

    def test_delete_affiliate_link_on_website(self):
        self.authenticate('portal', 'portal')
        res = self.url_open(self.base_url + '/affiliate')
        csrf_token = html.fromstring(res.content).xpath("//input[@name='csrf_token']")[0].value

        affiliate_link_admin = self.env['link.tracker'].with_user(self.user_admin).create({
            'url': 'http://localhost:8000',
            'affiliate_code_id': self.affiliate_code_admin.id
        })
        affiliate_link_portal = self.env['link.tracker'].with_user(self.user_portal).sudo().create({
            'url': 'http://localhost:8000',
            'affiliate_code_id': self.user_portal.affcode_ids.id
        })

        # case: can't delete other's affiliate link
        res = self.opener.post(self.base_url + '/affiliate/remove_link/%s' % affiliate_link_admin.id, data={
            'csrf_token': csrf_token
        })
        self.assertTrue(affiliate_link_admin.exists())
        self.assertEqual(res.status_code, 403)

        # case: only can delete its own link
        res = self.opener.post(self.base_url + '/affiliate/remove_link/%s' % affiliate_link_portal.id, data={
            'csrf_token': csrf_token
        })
        self.assertFalse(affiliate_link_portal.exists())
        self.assertEqual(res.status_code, 200)

        # case: delete link not exist
        res = self.opener.post(self.base_url + '/affiliate/remove_link/8888888', data={
            'csrf_token': csrf_token
        })
        self.assertEqual(res.status_code, 403)

    def test_update_affiliate_link_on_website(self):
        self.authenticate('admin', 'admin')
        res = self.url_open(self.base_url + '/affiliate')
        csrf_token = html.fromstring(res.content).xpath("//input[@name='csrf_token']")[0].value

        affiliate_link_admin = self.env['link.tracker'].with_user(self.user_admin).create({
            'title': 'admin link',
            'url': 'http://localhost:8000',
            'affiliate_code_id': self.affiliate_code_admin.id
        })
        affiliate_link_portal = self.env['link.tracker'].with_user(self.user_portal).sudo().create({
            'title': 'portal link',
            'url': 'http://localhost:8000',
            'affiliate_code_id': self.user_portal.affcode_ids.id
        })

        # case: can't update other's affiliate link
        res = self.opener.post(self.base_url + '/affiliate/update_link/%s' % affiliate_link_portal.id, data={
            'csrf_token': csrf_token,
            'new_name': 'title test',
            'new_medium': self.env.ref('utm.utm_medium_facebook').id,
            'new_source': self.env.ref('utm.utm_source_facebook').id
        })
        self.assertEqual(affiliate_link_portal.title, 'portal link')
        self.assertEqual(res.status_code, 403)

        # case: only can update its own link
        res = self.opener.post(self.base_url + '/affiliate/update_link/%s' % affiliate_link_admin.id, data={
            'csrf_token': csrf_token,
            'new_name': 'title test',
            'new_medium': self.env.ref('utm.utm_medium_facebook').id,
            'new_source': self.env.ref('utm.utm_source_facebook').id
        })
        self.env['link.tracker'].invalidate_cache(['title'], affiliate_link_admin.ids)
        self.assertEqual(affiliate_link_admin.title, 'title test')
        self.assertEqual(affiliate_link_admin.medium_id.id, self.env.ref('utm.utm_medium_facebook').id)
        self.assertEqual(affiliate_link_admin.source_id.id, self.env.ref('utm.utm_source_facebook').id)
        self.assertEqual(res.status_code, 200)

        # case: update link not exist
        res = self.opener.post(self.base_url + '/affiliate/update_link/8888888', data={
            'csrf_token': csrf_token,
            'new_name': 'title test',
            'new_medium': self.env.ref('utm.utm_medium_facebook').id,
            'new_source': self.env.ref('utm.utm_source_facebook').id
        })
        self.assertEqual(res.status_code, 403)
