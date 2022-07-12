from odoo.tests import SavepointCase, tagged
from odoo.exceptions import ValidationError

@tagged('post_install', '-at_install')
class TestFeeDefinition(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestFeeDefinition, cls).setUpClass()
        cls.product_product_demo1 = cls.env.ref('product.product_product_1')
        cls.product_product_demo2 = cls.env.ref('product.product_product_2')
    
    def test_create_nested_fee_definition(self):
        "Add direct fee product_demo1 for product_demo2"
        self.fee_apply_to_service_01 = self.env['fee.definition'].create({
            'product_tmpl_id': self.product_product_demo2.product_tmpl_id.id,
            'product_id': self.product_product_demo1.id,
            'quantity': 2,
            })
        with self.assertRaises(ValidationError):
            "Add direct fee product_demo1 for product_demo1"
            self.fee_apply_to_service_01 = self.env['fee.definition'].create({
                'product_tmpl_id': self.product_product_demo1.product_tmpl_id.id,
                'product_id': self.product_product_demo1.id,
                'quantity': 2,
                })
