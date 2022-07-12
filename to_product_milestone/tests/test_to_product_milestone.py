try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    import psycopg2
    UniqueViolation = psycopg2.IntegrityError

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger


@tagged('post_install', '-at_install')
class TestToProductMilestone(TransactionCase):

    def setUp(self):
        super(TestToProductMilestone, self).setUp()
        self.product_milestone1 = self.env['product.milestone'].create({
            'name': 'Product Milestone Test',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'amount': 1
        })

    @mute_logger('odoo.sql_db')
    def test_constraints(self):
        # case 1: Test constraint unique(amount, uom_id)
        self.env['product.milestone'].create({
            'name': 'Product Milestone Test 2',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'amount': 12
        })

        with self.assertRaises(UniqueViolation):
            self.env['product.milestone'].create({
                'name': 'Product Milestone Test 2',
                'uom_id': self.env.ref('uom.product_uom_unit').id,
                'amount': 1
            })

    def test_name_get(self):
        self.product_milestone1.amount = 2
        self.assertEqual(self.product_milestone1.name_get()[0][1], 'Product Milestone Test [2 Units]')

        self.product_milestone1.name = 'Produck Test'
        self.assertEqual(self.product_milestone1.name_get()[0][1], 'Produck Test [2 Units]')

    def test_access_right(self):
        user1 = self.env['res.users'].create({
            'name': 'User t1',
            'login': 'User t1',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        manager = self.env['res.users'].create({
            'name': 'Product Milestone Manager',
            'login': 'Product Milestone Manager',
            'groups_id': [(6, 0, [self.env.ref('to_product_milestone.group_product_milestone_manager').id])]
        })

        # case 2:
        self.product_milestone1.with_user(user1).read()
        with self.assertRaises(AccessError):
            self.product_milestone1.with_user(user1).name = 'Produck'
        with self.assertRaises(AccessError):
            self.env['product.milestone'].with_user(user1).create({
                'name': 'Product Mineestone 1',
                'uom_id': self.env.ref('uom.product_uom_unit').id,
                'amount': 21
            })

        # case 3:
        self.product_milestone1.with_user(manager).read()
        self.product_milestone1.with_user(manager).name = 'Produck'
        self.env['product.milestone'].with_user(manager).create({
            'name': 'Product Mineestone 1',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'amount': 21
        })
