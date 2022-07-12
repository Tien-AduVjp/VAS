from psycopg2 import IntegrityError

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


@tagged('post_install', '-at_install')
class TestToProductCollection(TransactionCase):

    def setUp(self):
        super(TestToProductCollection, self).setUp()
        self.product_collection_1 = self.env['product.collection'].create({
            'name': 'Product collection test 1'
        })
        self.product_collection_2 = self.env['product.collection'].create({
            'name': 'Product collection test 2'
        })
        self.product_1 = self.env['product.template'].create({
            'name': 'Produck test 1'
        })

    def test_constraint_name_unique(self):
        # case 1: Test constraint  name_unique
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['product.collection'].create({
                'name': self.product_collection_1.name
            })

    def test_constraint_name_description_check(self):
        # case 2: Test constraint name_description_check
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['product.collection'].create({
                'name': 'test',
                'description': 'test'
            })

    def test_unlink_product_collection(self):
        # case 3: Test unlink product collection
        self.product_1.collection_id = self.product_collection_1
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.product_collection_1.unlink()

    def test_access_right(self):
        # case 4: test access right
        user_1 = self.env['res.users'].create({
            'name': 'user1',
            'login': 'user test 1',
            'groups_id': [(6, 0, self.env.ref('base.group_user').ids)]
        })
        user_2 = self.env['res.users'].create({
            'name': 'user2',
            'login': 'user test 2',
            'groups_id': [(6, 0, self.env.ref('base.group_portal').ids)]
        })

        product_collection = self.env['product.collection'].with_user(user_1).create({
            'name': 'function 1'
        })
        product_collection.with_user(user_1).read()
        product_collection.with_user(user_1).name = 'test'
        product_collection.with_user(user_1).unlink()

        with self.assertRaises(AccessError):
            self.env['product.collection'].with_user(user_2).create({
                'name': 'function 2'
            })
        with self.assertRaises(AccessError):
            self.product_collection_1.with_user(user_2).read()
        with self.assertRaises(AccessError):
            self.product_collection_1.with_user(user_2).name = 'test'
        with self.assertRaises(AccessError):
            self.product_collection_1.with_user(user_2).unlink()

    def test_compute_products_count(self):
        # case 5: test compute_products_count
        self.env['product.template'].create({
            'name': 'produck1',
            'collection_id': self.product_collection_1.id
        })
        self.env['product.template'].create({
            'name': 'produck2',
            'collection_id': self.product_collection_1.id
        })

        self.assertEqual(self.product_collection_1.products_count, 2)
        self.assertEqual(self.product_collection_2.products_count, 0)
