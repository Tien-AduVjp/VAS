from odoo.tests import tagged

from odoo.addons.to_shorten_url.tests.shorten_url_common import ShortenURLCommon


@tagged('post_install', '-at_install')
class TestDescShortLink(ShortenURLCommon):

    @classmethod
    def setUpClass(cls):
        super(TestDescShortLink, cls).setUpClass()

        cls.product = cls.env.ref('product.product_delivery_01')

        cls.so = cls.env.ref('sale.sale_order_5')

        cls.order_line_greater_60 = cls.env['sale.order.line'].create({
            'product_id': cls.product.id,
            'order_id': cls.so.id,
            'name': cls.link_greater_60
            })
        cls.order_line_less_than_60 = cls.env['sale.order.line'].create({
            'product_id': cls.product.id,
            'order_id': cls.so.id,
            'name': cls.link_less_than_60
            })
        cls.order_line_link_greater_60_in_text = cls.env['sale.order.line'].create({
            'product_id': cls.product.id,
            'order_id': cls.so.id,
            'name': cls.link_greater_60_in_text
            })
        cls.order_line_link_less_than_60_in_text = cls.env['sale.order.line'].create({
            'product_id': cls.product.id,
            'order_id': cls.so.id,
            'name': cls.link_less_than_60_in_text
            })

    def test_create_link_greater_60(self):
        self.assertNotEqual(self.order_line_greater_60.name, self.link_greater_60 , "Link is not shortened in spite of long link greater 60")

    def test_create_link_less_than_60(self):
        self.assertEqual(self.order_line_less_than_60.name, self.link_less_than_60, "Link is shortened in spite of long link less than 60")

    def test_write_link_greater_60(self):
        self.order_line_greater_60.write({'name': self.link_greater_60}) 
        self.assertNotEqual(self.order_line_greater_60.name, self.link_greater_60, "Link is not shortened in spite of long link greater 60")

    def test_write_link_less_than_60(self):
        self.order_line_less_than_60.write({'name': self.link_less_than_60})
        self.assertEqual(self.order_line_less_than_60.name , self.link_less_than_60, "Link is shortened in spite of long link less than 60")
        
    def test_create_link_greater_60_in_text(self):
        self.assertNotEqual(self.order_line_link_greater_60_in_text.name, self.link_greater_60_in_text , "Inside a text, link is not shortened in spite of long link greater 60")

    def test_create_link_less_than_60_in_text(self):
        self.assertEqual(self.order_line_link_less_than_60_in_text.name, self.link_less_than_60_in_text, "Inside a text, link is shortened in spite of long link less than 60")
