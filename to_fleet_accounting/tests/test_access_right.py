from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install', 'access_right')
class TestAccessRight(Common):
    
    @classmethod
    def setUpClass(cls):
        super(TestAccessRight, cls).setUpClass()
        
        User = cls.env['res.users'].with_context(no_reset_password=True,tracking_disable=True)
        
        cls.user_account_invoice = User.create({
                'name': 'user invoicing',
                'login': 'user invoicing',
                'email': 'userinvocing@example.viindoo.com',
                'groups_id': [(6, 0, [cls.env.ref('account.group_account_invoice').id])]
            })
        
        cls.user_account_user = User.create({
                'name': 'user account user',
                'login': 'user account user',
                'email': 'useraccountuser@example.viindoo.com',
                'groups_id': [(6, 0, [cls.env.ref('account.group_account_user').id])]
            })
    
    def test_access_invoicing_user(self):
        # Vehicle(1,0,0,0)
        vehicle = self.vehicle_1.with_user(self.user_account_invoice)
        vehicle.name # User Invoicing only need access to read vehicle
        self.assertRaises(AccessError, vehicle.write, {'name': 'SH'})
        self.assertRaises(AccessError, vehicle.create, {'name': 'SH'})
        self.assertRaises(AccessError, vehicle.unlink)
        
        # Vehicle Cost(1,1,1,0) (Only with cost created by himself)
        cost_himself = self.generate_cost_vehicle(self.vehicle_1, self.service_1, self.vendor_1, user_created=self.user_account_invoice)
        cost_himself.read()
        cost_himself.write({'name': 'clean'})
        self.assertRaises(AccessError, cost_himself.unlink)
        # Cost created by other user
        cost_other_user = self.generate_cost_vehicle(self.vehicle_1, self.service_1, self.vendor_1).with_user(self.user_account_invoice)
        self.assertRaises(AccessError, cost_other_user.read)
        self.assertRaises(AccessError, cost_other_user.write, {'name': 'clean'})
        self.assertRaises(AccessError, cost_other_user.unlink)
        
        # Service type(1,0,0,0)
        service = self.service_1.with_user(self.user_account_invoice)
        service.read()
        self.assertRaises(AccessError, service.write, {'name': 'clean'})
        self.assertRaises(AccessError, service.create, {'name': 'clean', 'category': 'service'})
        self.assertRaises(AccessError, service.unlink)

    def test_access_account_user(self):
        # Service type(1,1,1,1)
        service = self.service_1.with_user(self.user_account_user)
        service.read()
        service.write({'name': 'clean'})
        service.create({'name': 'clean', 'category': 'service'})
        service.unlink()
