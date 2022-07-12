from odoo.tests.common import SavepointCase, Form, tagged
from odoo.tools.misc import mute_logger


@tagged('post_install', '-at_install')
class TestPriceLock(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPriceLock, cls).setUpClass()
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.order = cls.env.ref('sale.sale_order_1')
        cls.user_demo.groups_id = [(4, cls.env.ref('sales_team.group_sale_salesman').id)]

    def test_change_price_unit(self):
        """ User user does not belong to Sale Price Modifying Group
            Do not allow to change price unit
        """
        self.assertNotIn(self.env.company.sales_price_modifying_group_id, self.user_demo.groups_id)
        form = Form(self.order.with_user(self.user_demo))
        with form.order_line.edit(0) as order_line, mute_logger('odoo.tests.common.onchange'):
            price_unit_origin = order_line.price_unit
            # modify price unit
            order_line.price_unit = price_unit_origin + 100
            # => this price unit does not change
            self.assertEqual(order_line.price_unit, price_unit_origin)

    def test_change_uom(self):
        """ User does not belong to Sale Price Modifying Group => Change UoM
            Expected result: price unit is recalculated according to the new uom
        """
        self.assertNotIn(self.env.company.sales_price_modifying_group_id, self.user_demo.groups_id)
        form = Form(self.order.with_user(self.user_demo))
        with form.order_line.edit(0) as order_line, mute_logger('odoo.tests.common.onchange'):
            price_unit_origin = order_line.price_unit
            # modify uom
            order_line.product_uom = self.env.ref('uom.product_uom_dozen')
            order_line.product_uom = self.env.ref('uom.product_uom_unit')
            self.assertEqual(order_line.price_unit, price_unit_origin)
