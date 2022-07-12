from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase, Form
from odoo.tools.misc import mute_logger
from odoo.tests import tagged

@tagged('post_install', '-at_install')
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

    def test_compute_length(self):
        self.product_tmp_1.product_variant_id.length = 200
        self.assertEqual(self.product_tmp_1.length, 200)

        product_tmp_copy = self.product_tmp_1.product_variant_id.copy()
        self.product_tmp_1.product_variant_ids = [(4, product_tmp_copy.id, 0)]
        self.assertEqual(self.product_tmp_1.length, 0)

        product_tmp_copy.active = False
        self.product_tmp_1.product_variant_id.length = 300
        self.assertEqual(self.product_tmp_1.length, 300)

    def test_compute_width(self):
        self.product_tmp_1.product_variant_id.width = 200
        self.assertEqual(self.product_tmp_1.width, 200)

        product_tmp_copy = self.product_tmp_1.product_variant_id.copy()
        self.product_tmp_1.product_variant_ids = [(4, product_tmp_copy.id, 0)]
        self.assertEqual(self.product_tmp_1.length, 0)

        product_tmp_copy.active = False
        self.product_tmp_1.product_variant_id.width = 300
        self.assertEqual(self.product_tmp_1.width, 300)

    def test_compute_height(self):
        self.product_tmp_1.product_variant_id.height = 200
        self.assertEqual(self.product_tmp_1.height, 200)

        product_tmp_copy = self.product_tmp_1.product_variant_id.copy()
        self.product_tmp_1.product_variant_ids = [(4, product_tmp_copy.id, 0)]
        self.assertEqual(self.product_tmp_1.length, 0)

        product_tmp_copy.active = False
        self.product_tmp_1.product_variant_id.height = 300
        self.assertEqual(self.product_tmp_1.height, 300)

    def test_compute_stowage_factor(self):
        self.product_tmp_1.product_variant_id.stowage_factor = 200
        self.assertEqual(self.product_tmp_1.stowage_factor, 200)

        product_tmp_copy = self.product_tmp_1.product_variant_id.copy()
        self.product_tmp_1.product_variant_ids = [(4, product_tmp_copy.id, 0)]
        self.assertEqual(self.product_tmp_1.length, 0)

        product_tmp_copy.active = False
        self.product_tmp_1.product_variant_id.stowage_factor = 300
        self.assertEqual(self.product_tmp_1.stowage_factor, 300)

    def test_inverse_length(self):
        self.product_tmp_1.write({
            'length': 2000
            })
        self.assertEqual(self.product_tmp_1.product_variant_ids.length, 2000)

    def test_inverse_width(self):
        self.product_tmp_1.write({
            'width': 2000
            })
        self.assertEqual(self.product_tmp_1.product_variant_ids.width, 2000)

    def test_inverse_height(self):
        self.product_tmp_1.write({
            'height': 2000
            })
        self.assertEqual(self.product_tmp_1.product_variant_ids.height, 2000)

    def test_inverse_stowage_factor(self):
        self.product_tmp_1.write({
            'stowage_factor': 2000
            })
        self.assertEqual(self.product_tmp_1.product_variant_ids.stowage_factor, 2000)

    def test_compute_volume(self):
        self.product_tmp_1.product_variant_ids.write({
            'length': 2000,
            'width': 2000,
            'height': 2000
            })
        self.assertEqual(self.product_tmp_1.product_variant_ids.volume, 8)

    def test_compute_stowage_volume(self):
        self.product_tmp_1.product_variant_ids.write({
            'volume': 8,
            'stowage_factor': 5
            })
        self.assertEqual(self.product_tmp_1.product_variant_ids.stowage_volume,40)
