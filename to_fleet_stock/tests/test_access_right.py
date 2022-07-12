from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRight, cls).setUpClass()

        user_group_stock_user = cls.env.ref('stock.group_stock_user')
        user_group_stock_manager = cls.env.ref('stock.group_stock_manager')
        Users = cls.env['res.users'].with_context({'tracking_disable': True})

        cls.user_stock_user = Users.create({
            'name': 'Pauline Poivraisselle',
            'login': 'pauline',
            'email': 'p.p@example.viindoo.com',
            'notification_type': 'inbox',
            'groups_id': [(6, 0, [user_group_stock_user.id])]})

        cls.user_stock_manager = Users.create({
            'name': 'Julie Tablier',
            'login': 'julie',
            'email': 'j.j@example.viindoo.com',
            'notification_type': 'inbox',
            'groups_id': [(6, 0, [user_group_stock_manager.id])]})

    def test_stock_user_access_vehicle(self):
        vehicle = self.vehicle.with_user(self.user_stock_user)
        vehicle.name

        with self.assertRaises(AccessError), self.cr.savepoint():
            vehicle.write({'name': 'car'})

        with self.assertRaises(AccessError), self.cr.savepoint():
            vehicle.create({'name': 'car'})

        with self.assertRaises(AccessError), self.cr.savepoint():
            vehicle.unlink()

    def test_stock_user_access_service_type(self):
        type_service = self.type_service.with_user(self.user_stock_user)
        type_service.read()

        with self.assertRaises(AccessError), self.cr.savepoint():
            type_service.write({'name': 'wash car'})

        with self.assertRaises(AccessError), self.cr.savepoint():
            type_service.create({'name': 'wash tires'})

        with self.assertRaises(AccessError), self.cr.savepoint():
            type_service.unlink()
