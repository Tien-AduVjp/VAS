from odoo.tests import tagged

from odoo.addons.to_affiliate.tests.test_common import TestAffiliateCommon


@tagged('post_install', '-at_install')
class TestAffiliateCommon(TestAffiliateCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAffiliateCommon, cls).setUpClass()
        cls.sale_order_1 = cls.setup_sale_order()

    @classmethod
    def setup_sale_order(cls):
        return cls.env['sale.order'].create({
            'partner_id': cls.user_internal_2.partner_id.id,
            'partner_invoice_id': cls.user_internal_2.partner_id.id,
            'partner_shipping_id': cls.user_internal_2.partner_id.id,
            'pricelist_id': cls.env.ref('product.list0').id,
            'affcode_id': cls.aff_code_1.id,
            'company_id': cls.company_1.id,
            'order_line': [(0, 0, {
                'product_id': cls.product_2.id,
                'name': cls.product_2.name,
                'product_uom_qty': 1.0,
                'price_unit': 45000000
            })]
        })

    @classmethod
    def prepare_commission_data(cls, partner=False, aff_code=None):
        res = super(TestAffiliateCommon, cls).prepare_commission_data(partner=partner, aff_code=aff_code)
        res.update(order_id=cls.setup_sale_order().id)
        return res

    @classmethod
    def prepare_commission_lines_data(cls):
        res = super(TestAffiliateCommon, cls).prepare_commission_lines_data()
        res.update(sale_order_line_id=cls.setup_sale_order().order_line.id)
        return res
