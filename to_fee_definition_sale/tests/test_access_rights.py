from odoo.tests import SavepointCase, tagged
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install', 'access_rights')
class TestFeeAccessRights(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestFeeAccessRights, cls).setUpClass()
        cls.user_demo = cls.env.ref('base.user_demo')

    def test_sale_man_crud_fee(self):
        self.user_demo.groups_id = [(6, 0, [self.env.ref('sales_team.group_sale_salesman').id])]
        FeeDefinition = self.env['fee.definition']
        fee_definition = FeeDefinition.create({
            'product_tmpl_id': self.env.ref('product.product_order_01').product_tmpl_id.id,
            'product_id': self.env.ref('product.product_product_1').id,
            'quantity': 1,
        })
        with self.assertRaises(AccessError):
            FeeDefinition.with_user(self.user_demo).create({
                'product_tmpl_id': self.env.ref('product.product_order_01').product_tmpl_id.id,
                'product_id': self.env.ref('product.product_product_1').id,
                'quantity': 1,
            })
            fee_definition = fee_definition.with_user(self.user_demo)
            fee_definition.quantity = 2
            fee_definition.unlink()

    def test_sale_manager_crud_fee(self):
        self.user_demo.groups_id = [(6, 0, [self.env.ref('sales_team.group_sale_manager').id])]
        fee_definition = self.env['fee.definition'].with_user(self.user_demo).create({
            'product_tmpl_id': self.env.ref('product.product_order_01').product_tmpl_id.id,
            'product_id': self.env.ref('product.product_product_1').id,
            'quantity': 1,
        })
        fee_definition.quantity = 3
        fee_definition.unlink()
