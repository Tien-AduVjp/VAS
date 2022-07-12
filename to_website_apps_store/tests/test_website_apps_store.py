from lxml import etree, html
from werkzeug.urls import url_parse

from odoo.tests import HttpCase, tagged, Form
from odoo.tools import mute_logger
from odoo import http
from odoo import fields

from odoo.addons.website.tools import MockRequest
from odoo.addons.http_routing.models.ir_http import slug
from ..controllers.main import WebsiteSale


@tagged('post_install', '-at_install', 'external', '-standard')
class TestAppStore(HttpCase):
    def setUp(self):
        super(TestAppStore, self).setUp()
        context_no_mail = {'tracking_disable': True}
        self.env = self.env(context=dict(context_no_mail, **self.env.context))
        self.base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.group_portal = self.env.ref('base.group_portal')
        self.website = self.env['website'].browse(1)
        self.category_all = self.env.ref('to_website_apps_store.prod_public_categ_odoo_apps')
        self.currency_usd_id = self.env.ref('base.USD').id
        self.bank_journal_usd = self.env['account.journal'].create(
            {'name': 'Bank Test', 'type': 'bank', 'code': 'BNKTEST', 'currency_id': self.env.company.currency_id.id})
        self.user_1 = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'Zed',
            'login': 'portalapps1@abc.com',
            'password': 'portalapps1',
            'groups_id': [(6, 0, [self.group_portal.id])]
        })
        self.user_2 = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'John Wick',
            'login': 'portalapps2@abc.com',
            'password': 'portalapps2',
            'groups_id': [(6, 0, [self.group_portal.id])]
        })
        self.partner_1 = self.user_1.partner_id
        self.partner_2 = self.user_2.partner_id

        self.odoo_version_12 = self.env['odoo.version'].search([('name', '=', '12.0')], limit=1)
        self.odoo_version_13 = self.env['odoo.version'].search([('name', '=', '13.0')], limit=1)

        REMOTE_URL = 'https://github.com/Viindoo/backend_theme.git'
        self.git_repo = self.env['git.repository'].create({
            'remote_url': REMOTE_URL,
            'name': 'Viindoo-backend_theme',
            'company_id': self.env.company.id,
        })

        self.git_branch_12 = self.env['git.branch'].create({
            'name': '12.0',
            'repository_id': self.git_repo.id,
            'odoo_version_id': self.odoo_version_12.id,
            'generate_app_products': True,
        })
        self.git_branch_13 = self.env['git.branch'].create({
            'name': '13.0',
            'repository_id': self.git_repo.id,
            'odoo_version_id': self.odoo_version_13.id,
            'generate_app_products': True,
        })
        self.module_base_12 = self.env['odoo.module.version'].create({
            'name': 'Module Base',
            'technical_name': 'module_base',
            'odoo_version_id': self.odoo_version_12.id,
            'git_branch_id': self.git_branch_12.id,
            'price_currency': 0,
            'currency_id': self.env.company.currency_id.id,
            'version': '0.1',
            'website_published': True,
            'public_categ_ids': [(6, 0, [self.env.ref('to_website_apps_store.prod_public_categ_odoo_apps').id])],
            'website_published_date': fields.Datetime.from_string('2020-07-03 02:30:30')
        })
        self.module_1_v12 = self.env['odoo.module.version'].create({
            'name': 'Module 1',
            'technical_name': 'module_1',
            'odoo_version_id': self.odoo_version_12.id,
            'git_branch_id': self.git_branch_12.id,
            'price_currency': 315000,
            'currency_id': self.env.company.currency_id.id,
            'version': '0.1',
            'website_published': True,
            'public_categ_ids': [(6, 0, [self.env.ref('to_website_apps_store.prod_public_categ_modules').id])],
            'website_published_date': fields.Datetime.from_string('2020-07-04 02:30:30'),
        })
        self.module_2_v12 = self.env['odoo.module.version'].create({
            'name': 'Module 2',
            'technical_name': 'module_2',
            'odoo_version_id': self.odoo_version_12.id,
            'git_branch_id': self.git_branch_12.id,
            'price_currency': 340000,
            'currency_id': self.env.company.currency_id.id,
            'version': '0.1',
            'depends': 'module_base,module_1',
            'website_published': True,
            'public_categ_ids': [(6, 0, [self.env.ref('to_website_apps_store.prod_public_categ_modules').id])],
            'website_published_date': fields.Datetime.from_string('2021-07-04 02:30:30')
        })
        self.module_3_v12 = self.env['odoo.module.version'].create({
            'name': 'Module 3',
            'technical_name': 'module_3',
            'odoo_version_id': self.odoo_version_12.id,
            'git_branch_id': self.git_branch_12.id,
            'price_currency': 43500,
            'currency_id': self.env.company.currency_id.id,
            'version': '0.1',
            'depends': 'module_1',
            'website_published': True,
            'public_categ_ids': [(6, 0, [self.env.ref('to_website_apps_store.prod_public_categ_discuss').id])],
            'website_published_date': fields.Datetime.from_string('2021-07-05 02:30:30')
        })
        self.module_4_v12 = self.env['odoo.module.version'].create({
            'name': 'Module 4',
            'technical_name': 'module_4',
            'odoo_version_id': self.odoo_version_12.id,
            'git_branch_id': self.git_branch_12.id,
            'price_currency': 13500,
            'currency_id': self.env.company.currency_id.id,
            'version': '0.3',
            'depends': 'module_2',
            'website_published': True,
            'public_categ_ids': [(6, 0, [self.env.ref('to_website_apps_store.prod_public_categ_discuss').id])],
            'website_published_date': fields.Datetime.from_string('2021-08-15 02:30:30')
        })
        self.module_5_v12 = self.env['odoo.module.version'].create({
            'name': 'Module 5',
            'technical_name': 'module_5',
            'odoo_version_id': self.odoo_version_12.id,
            'git_branch_id': self.git_branch_12.id,
            'price_currency': 10000,
            'currency_id': self.env.company.currency_id.id,
            'version': '0.2',
            'depends': 'module_3,module_4',
            'website_published': True,
            'public_categ_ids': [(6, 0, [self.env.ref('to_website_apps_store.prod_public_categ_ecommerce').id])],
            'website_published_date': fields.Datetime.now()
        })

    def create_sale_order(self, partner, modules=None):
        modules = modules or []
        order_lines = []
        for module in modules:
            order_line = {
                'product_id': module.product_id.id,
                'name': module.product_id.name,
                'product_uom_qty': 1.0,
                'price_unit': module.price_currency,
                # In odoo 14, `delivery` is the default value of the field 'invoice_policy', it is applied to any new product created,
                # so need to set qty_delivered=1 to generate invoice.
                'qty_delivered': 1,
            }
            order_lines.append([0, 0, order_line])
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'company_id': self.env.company.id,
            'state': 'sale',
            'order_line': order_lines
        })
        sale_order.onchange_partner_id()
        sale_order._compute_odoo_module_versions()
        sale_order._onchange_order_line_for_apps()
        sale_order._create_invoices()
        return sale_order

    def register_payment(self, invoice):
        invoice.action_post()
        action_data = invoice.action_register_payment()
        wizard = Form(self.env['account.payment.register'].with_context(action_data['context'])).save()
        wizard.with_context({'dont_redirect_to_payments': True})._create_payments()

    def test_user_did_not_buy_redirect(self):
        # redirect to /my when attempting to access download url
        self.group_portal = self.env.ref('base.group_portal')
        self.authenticate('portalapps2@abc.com', 'portalapps2')
        res = self.opener.get(self.base_url + '/my/apps/download/%s' % self.module_5_v12.id)
        self.assertEqual(res.status_code, 200)
        path = url_parse(res.url).path
        self.assertEqual(path, '/my')

    def test_user_bought_apps_download(self):
        order = self.create_sale_order(self.partner_1, [self.module_1_v12])
        self.register_payment(order.invoice_ids[:1])
        self.authenticate('portalapps1@abc.com', 'portalapps1')
        # can download
        res = self.url_open(self.base_url + '/my/apps/download/%s' % self.module_1_v12.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('content-type', '').lower(), 'application/zip',
                         'Test download paid apps failed')
        # module unpublished => still can download
        self.module_1_v12.website_published = False
        res = self.url_open(self.base_url + '/my/apps/download/%s' % self.module_1_v12.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Content-Type'], 'application/zip')

        # module is archived => still can download
        self.module_1_v12.website_published = True
        self.module_1_v12.active = False
        res = self.url_open(self.base_url + '/my/apps/download/%s' % self.module_1_v12.id)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Content-Type'], 'application/zip')

    def test_button_visible_on_page_details(self):
        # Buy it but don't buy the app it depends on => show button add to cart
        order = self.create_sale_order(self.partner_1, [self.module_5_v12])
        self.register_payment(order.invoice_ids[:1])
        self.authenticate('portalapps1@abc.com', 'portalapps1')
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_5_v12.technical_name)
        self.assertEqual(res.status_code, 200)
        root = etree.fromstring(res.content.decode(), etree.HTMLParser())
        button = root.xpath("//*[@id='btn_module_add_to_cart']")
        self.assertEqual(len(button), 1, 'Show button add to cart')

        # Buy the app it depends on => show button download
        order = self.create_sale_order(self.partner_1, [self.module_1_v12, self.module_2_v12, self.module_3_v12, self.module_4_v12, self.module_base_12])
        self.register_payment(order.invoice_ids[:1])
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_5_v12.technical_name)
        self.assertEqual(res.status_code, 200)
        root = etree.fromstring(res.content.decode(), etree.HTMLParser())
        button = root.xpath("//*[@id='btn_module_download']")
        self.assertEqual(len(button), 1, 'Show button download')
        self.assertEqual(button[0].attrib.get('href'), '/my/apps/download/%s' % self.module_5_v12.id, 'Show button download')
        self.logout()

        # did not buy => show button add to cart
        self.authenticate('portalapps2@abc.com', 'portalapps2')
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_5_v12.technical_name)
        self.assertEqual(res.status_code, 200)
        root = etree.fromstring(res.content.decode(), etree.HTMLParser())
        button = root.xpath("//*[@id='btn_module_add_to_cart']")
        self.assertEqual(len(button), 1, 'Show button add to cart')
        self.logout()

        # user has group odoo module user => show button download
        self.user_2.groups_id = [(6, 0, [self.env.ref('to_odoo_module.odoo_module_user').id])]
        self.authenticate('portalapps2@abc.com', 'portalapps2')
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_5_v12.technical_name)
        self.assertEqual(res.status_code, 200)
        root = etree.fromstring(res.content.decode(), etree.HTMLParser())
        button = root.xpath("//*[@id='btn_module_download']")
        self.assertEqual(len(button), 1, 'Show button download')
        self.logout()

    def test_search_module(self):
        # search by version
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_base_12.technical_name)
        self.assertEqual(res.status_code, 200)

        res = self.url_open(self.base_url + '/apps/app/14.0/%s' % self.module_base_12.technical_name)
        self.assertEqual(res.status_code, 404)

    def test_module_public(self):
        self.git_branch_12.visible_on_apps_store = False
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_base_12.technical_name)
        self.assertEqual(res.status_code, 404)

        self.git_branch_12.visible_on_apps_store = True
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_base_12.technical_name)
        self.assertEqual(res.status_code, 200)

        domain = self.website._sale_app_domain(category_id=self.category_all)

        self.module_base_12.product_id.sale_ok = False
        modules = self.env['odoo.module.version'].search(domain)
        self.assertNotIn(self.module_base_12, modules)

    def test_get_top_modules_most_downloaded(self):
        self.module_5_v12.external_downloads_count = 15
        self.module_4_v12.external_downloads_count = 5
        self.module_3_v12.external_downloads_count = 3
        domain = self.website._sale_app_domain(category_id=self.category_all)
        modules = self.env['odoo.module.version'].search(domain)
        sorted_modules = self.category_all.get_most_download_odoo_modules(search=modules, limit=6)
        self.assertEqual(sorted_modules[0], self.module_5_v12)
        self.assertEqual(sorted_modules[2], self.module_3_v12)

    def test_get_newest_modules(self):
        domain = self.website._sale_app_domain(category_id=self.category_all)
        modules = self.env['odoo.module.version'].search(domain)
        sorted_modules = self.category_all.get_new_odoo_modules(search=modules, limit=6)
        self.assertEqual(sorted_modules[0], self.module_5_v12)
        self.assertEqual(sorted_modules[-1], self.module_base_12)

    def test_get_relevant_modules(self):
        # assuming the user has viewed this category before
        public_category = self.env['product.public.category'].create({
            'name': 'Category Test',
            'parent_id': self.env.ref('to_website_apps_store.prod_public_categ_odoo_apps').id
        })
        self.module_5_v12.public_categ_ids = [(6, 0, public_category.ids)]
        self.module_5_v12.flush()
        cookies = {
            'fav_categ': public_category.name
        }
        self.url_open(self.base_url + '/apps/category/%s' % slug(public_category))
        with MockRequest(self.env, website=self.website, context={'lang': 'en_US'}, cookies=cookies):
            domain = self.website._sale_app_domain(category_id=self.category_all)
            modules = self.env['odoo.module.version'].search(domain)
            sorted_modules = self.category_all.get_top_odoo_modules(search=modules, limit=6)
            self.assertEqual(sorted_modules[0], self.module_5_v12)

    def test_get_top_purchase_modules(self):
        self.create_sale_order(self.partner_1, [self.module_1_v12])
        self.create_sale_order(self.partner_2, [self.module_1_v12])
        self.create_sale_order(self.partner_1, [self.module_1_v12])
        self.module_1_v12.flush()
        self.create_sale_order(self.partner_1, [self.module_base_12])
        self.create_sale_order(self.partner_2, [self.module_base_12])
        self.module_4_v12.flush()
        domain = self.website._sale_app_domain(category_id=self.category_all)
        modules = self.env['odoo.module.version'].search(domain)
        with MockRequest(self.env, website=self.website):
            sorted_modules = WebsiteSale()._get_purchases_ids(odoo_module_versions=modules, limit=6, offset=0)
        self.assertEqual(sorted_modules[0], self.module_1_v12)
        self.assertEqual(sorted_modules[1], self.module_base_12)

    def test_add_to_cart_update_dependencies(self):
        res = self.url_open(self.base_url + '/apps/app/12.0/%s' % self.module_5_v12.technical_name)
        root = etree.fromstring(res.content.decode(), etree.HTMLParser())
        csrf_token = root.xpath("//input[@name='csrf_token']")[0].attrib.get('value')
        product_id = root.xpath("//input[@name='product_id']")[0].attrib.get('value')
        data = {
            'product_id': product_id,
            'csrf_token': csrf_token,
        }
        res = self.opener.post(self.base_url + '/shop/cart/update', data=data)
        root = etree.fromstring(res.content.decode(), etree.HTMLParser())
        order_id = root.xpath("//li[contains(@class, 'o_wsale_my_cart')]//sup")[0].attrib.get('data-order-id')
        sale_order = self.env['sale.order'].browse(int(order_id))
        # update dependencies
        self.assertEqual(len(sale_order.order_line), 6)
        self.assertEqual(sale_order.order_line.product_id.odoo_module_version_id.sorted('technical_name').mapped(
            'technical_name'), ['module_1', 'module_2', 'module_3', 'module_4', 'module_5', 'module_base'])
        # remove parent module => auto update again
        sale_order._cart_update(product_id=self.module_3_v12.product_id.id, add_qty=None, set_qty=0)
        self.assertEqual(len(sale_order.order_line), 6)
        # remove child module => Ok
        sale_order._cart_update(product_id=self.module_5_v12.product_id.id, add_qty=None, set_qty=0)
        self.assertEqual(len(sale_order.order_line), 5)

    def test_rating_module(self):
        def prepare_rating_values(module_version_id, rating_value):
            return {
                'csrf_token': http.WebRequest.csrf_token(self),
                'message': 'Rating module appstore',
                'res_model': 'odoo.module.version',
                'res_id': module_version_id,
                'rating_value': rating_value
            }

        def rating_module(data_rating):
            res = self.opener.post(self.base_url + '/mail/chatter_post', data=data_rating)
            return res

        # did not buy
        self.authenticate(None, None)
        data = prepare_rating_values(self.module_2_v12.id, 10)
        rating_result = rating_module(data)
        p = html.fromstring(rating_result.content).xpath("//div[@id='wrap']//p")[0]
        message = self.env['mail.message'].search([('res_id', '=', self.module_2_v12.id),
                                                   ('body', '=', '<p>Rating module appstore</p>'),
                                                   ('author_id', '=', self.partner_2.id)])
        self.assertEqual(url_parse(rating_result.url).path, '/mail/chatter_post')
        self.assertEqual(p.text_content(), 'You may not be able to rate an app that you did not buy.')
        self.assertFalse(message, 'Rating OK')

        # user bought app
        order = self.create_sale_order(self.partner_1, [self.module_1_v12])
        self.register_payment(order.invoice_ids[:1])
        self.authenticate('portalapps1@abc.com', 'portalapps1')
        data = prepare_rating_values(self.module_1_v12.id, 5)
        rating_module(data)
        message = self.env['mail.message'].search([('res_id', '=', self.module_1_v12.id),
                                                   ('body', '=', '<p>Rating module appstore</p>'),
                                                   ('author_id', '=', self.partner_1.id)])
        self.assertTrue(message, 'Cannot rating this module')
        self.logout()

        # user has group odoo apps manager
        self.user_2.groups_id = [(6, 0, [self.env.ref('to_odoo_module.odoo_module_manager').id])]
        self.authenticate('portalapps2@abc.com', 'portalapps2')
        data = prepare_rating_values(self.module_2_v12.id, 5)
        rating_result = rating_module(data)
        p = html.fromstring(rating_result.content).xpath("//div[@id='wrap']//p")[0]
        message = self.env['mail.message'].search([('res_id', '=', self.module_2_v12.id),
                                                   ('body', '=', '<p>Rating module appstore</p>'),
                                                   ('author_id', '=', self.partner_2.id)])
        self.assertEqual(url_parse(rating_result.url).path, '/mail/chatter_post')
        self.assertEqual(p.text_content(), 'You may not be able to rate an app that you did not buy.')
        self.assertFalse(message, 'Rating OK')
        self.logout()
