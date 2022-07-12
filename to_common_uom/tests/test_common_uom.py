from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, Form


@tagged('post_install', '-at_install')
class TestCommonUom(TransactionCase):

    def setUp(self):
        super(TestCommonUom, self).setUp()
        UoM = self.env['uom.uom']

        self.category_time = self.env['uom.category'].create({
            'name': 'Time'
        })
        self.category_unit = self.env['uom.category'].create({
            'name': 'Units'
        })
        self.uom_days = UoM.create({
            'name': 'Days',
            'category_id': self.category_time.id
        })
        self.uom_years = UoM.create({
            'name': 'Years',
            'category_id': self.category_time.id,
            'uom_type': 'bigger'
        })
        self.uom_unit = UoM.create({
            'name': 'Unit',
            'category_id': self.category_unit.id
        })
        self.product1 = self.env['product.template'].create({
            'name': 'Product 1'
        })

    def test_onchange_uom_id(self):
        with Form(self.env['product.template']) as product_form:
            product_form.name = 'Product Form'
            product_form.uom_id = self.uom_days
            self.assertEqual(product_form.uom_id, product_form.uom_3rd_id)

    def test_constraint_check_uom(self):
        self.product1.uom_id = self.uom_days
        # case 1: two uom product1.uom_id and product1.uom_3rd_id with same category_id will not raise error
        self.product1.uom_3rd_id = self.uom_years
        # case 2: two uom product1.uom_id and product1.uom_3rd_id different category_id will raise error
        with self.assertRaises(ValidationError):
            self.product1.uom_3rd_id = self.uom_unit
