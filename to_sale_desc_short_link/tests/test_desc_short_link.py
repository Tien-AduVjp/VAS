from odoo.tests import tagged
from . import common

@tagged('post_install', '-at_install')
class TestToSaleDescShortLink(common.ToSaleDescShortLinkCommon):

    @classmethod
    def setUpClass(cls):
        super(TestToSaleDescShortLink, cls).setUpClass()

        cls.product = cls.env.ref('product.product_delivery_01')

        cls.so = cls.env.ref('sale.sale_order_5')

        cls.order_line_link_url_standalone = cls.env['sale.order.line'].create({
            'product_id': cls.product.id,
            'order_id': cls.so.id,
            'name': cls.link_url_standalone
            })
        cls.order_line_link_url_in_text = cls.env['sale.order.line'].create({
            'product_id': cls.product.id,
            'order_id': cls.so.id,
            'name': cls.link_url_in_text
            })

    def test_create_link_url_standalone(self):
        self.assertNotEqual(self.order_line_link_url_standalone.name, self.link_url_standalone , "Link (url standalone) is not shortened in create ")

    def test_write_link_url_standalone(self):
        self.order_line_link_url_standalone.write({'name': self.link_url_standalone})
        self.assertNotEqual(self.order_line_link_url_standalone.name, self.link_url_standalone, "Link (url standalone) is not shortened in write")

    def test_create_link_url_in_text(self):
        self.assertNotEqual(self.order_line_link_url_in_text.name, self.link_url_in_text , "Inside a text, link is not shortened in create")

    def test_write_link_url_in_text(self):
        self.order_line_link_url_in_text.write({'name': self.link_url_in_text})
        self.assertNotEqual(self.order_line_link_url_in_text.name, self.link_url_in_text, "Inside a text, link is not shortened in write")
