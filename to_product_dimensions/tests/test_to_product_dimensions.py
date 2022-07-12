from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase, Form
from odoo.tools.misc import mute_logger


class TestToProductDimensions(TransactionCase):

    def setUp(self):
        super(TestToProductDimensions, self).setUp()
        self.product_tmp_1 = self.env['product.template'].create({
            'name': 'produck test 1',
            'uom_id': self.env.ref('uom.product_uom_categ_unit').id
        })
        self.product_tmp_2 = self.env['product.template'].create({
            'name': 'produck test 2',
            'uom_id': self.env.ref('uom.product_uom_categ_unit').id
        })

    @mute_logger('odoo.sql_db')
    def test_constraint_length(self):
        # case 1:
        # test write
        self.product_tmp_1.length = 1
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.product_tmp_1.write({'length':-1})
        # test create
        with self.assertRaises(IntegrityError):
            self.env['product.template'].create({
                'name': 'produck test 3',
                'uom_id': self.env.ref('uom.product_uom_categ_unit').id,
                'length':-1
                })

    @mute_logger('odoo.sql_db')
    def test_constraint_width(self):
        # case 2:
        # test write
        self.product_tmp_1.width = 1
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.product_tmp_1.write({'width':-1})
        # test create
        with self.assertRaises(IntegrityError):
            self.env['product.template'].create({
                'name': 'produck test 3',
                'uom_id': self.env.ref('uom.product_uom_categ_unit').id,
                'width':-1
                })

    @mute_logger('odoo.sql_db')
    def test_constraint_height(self):
        # case 3:
        # test write
        self.product_tmp_1.height = 1
        with self.assertRaises(IntegrityError), self.env.cr.savepoint():
            self.product_tmp_1.write({'height':-1})
        # test create
        with self.assertRaises(IntegrityError):
            self.env['product.template'].create({
                'name': 'produck test 3',
                'uom_id': self.env.ref('uom.product_uom_categ_unit').id,
                'height':-1
                })

    def test_onchange_dimensions(self):
        # case 4:
        product_form = Form(self.env['product.template'])
        product_form.name = 'Produck test'
        product_form.volume = 12

        product_form.width = 100000
        product_form.length = 100000

        self.assertEqual(product_form.volume, 12)

        product_form.height = 1200
        self.assertEqual(product_form.volume, 12000)

    def test_view_visibility(self):
        # case 5:
        product_form = Form(self.env['product.template'])
        product_form.name = 'Produck test'

        product_form.type = 'consu'
        self.assertEqual(product_form._get_modifier('height', 'invisible'), False)
        self.assertEqual(product_form._get_modifier('width', 'invisible'), False)
        self.assertEqual(product_form._get_modifier('length', 'invisible'), False)

        product_form.type = 'product'
        self.assertEqual(product_form._get_modifier('height', 'invisible'), False)
        self.assertEqual(product_form._get_modifier('width', 'invisible'), False)
        self.assertEqual(product_form._get_modifier('length', 'invisible'), False)

    def test_compute_default_length(self):
        self.product_tmp_1.product_variant_id.length = 200
        self.assertEqual(self.product_tmp_1.length, 200)

        self.product_tmp_1.product_variant_ids = [(4, self.product_tmp_1.product_variant_id.copy().id, 0)]
        self.assertEqual(self.product_tmp_1.length, 0)
