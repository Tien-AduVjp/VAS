from psycopg2 import IntegrityError

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.misc import mute_logger


@tagged('post_install', '-at_install')
class TestToProductFunction(TransactionCase):

    def setUp(self):
        super(TestToProductFunction, self).setUp()
        self.product_func_1 = self.env['product.function'].create({
            'name': 'Product function test 1'
        })
        self.product_func_2 = self.env['product.function'].create({
            'name': 'Product function test 2'
        })
        self.product_1 = self.env['product.template'].create({
            'name': 'produck test 1'
        })

    @mute_logger('odoo.sql_db')
    def test_constraint_name_unique(self):
        # case 2: test constraint  name_unique
        with self.assertRaises(IntegrityError):
            self.env['product.function'].create({
                'name': self.product_func_1.name
            })

    @mute_logger('odoo.sql_db')
    def test_constraint_name_description_check(self):
        # case 3: test constraint name_description_check
        with self.assertRaises(IntegrityError):
            self.env['product.function'].create({
                'name': 'test 1',
                'description': 'test 1'
            })

    @mute_logger('odoo.sql_db')
    def test_unlink_product_function(self):
        # case 5: delete product function
        self.product_1.function_id = self.product_func_1
        with self.assertRaises(IntegrityError):
            self.product_func_1.unlink()

    def test_access_right(self):
        # case 7: test access right
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

        product_func = self.env['product.function'].with_user(user_1).create({
            'name': 'function 1'
        })
        product_func.with_user(user_1).read()
        product_func.with_user(user_1).name = 'test'
        product_func.with_user(user_1).unlink()

        with self.assertRaises(AccessError):
            self.env['product.function'].with_user(user_2).create({
                'name': 'function 2'
            })
        with self.assertRaises(AccessError):
            self.product_func_1.with_user(user_2).read()
        with self.assertRaises(AccessError):
            self.product_func_1.with_user(user_2).name = 'test'
        with self.assertRaises(AccessError):
            self.product_func_1.with_user(user_2).unlink()

    def test_compute_products_count(self):
        # case 8: test _compute_products_count
        self.env['product.template'].create({
            'name': 'produck1',
            'function_id': self.product_func_1.id
        })
        self.env['product.template'].create({
            'name': 'produck2',
            'function_id': self.product_func_1.id
        })

        self.assertEqual(self.product_func_1.products_count, 2)
        self.assertEqual(self.product_func_2.products_count, 0)
