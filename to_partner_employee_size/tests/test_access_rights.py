from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('access_rights')
class TestAccessRights(TransactionCase):
    
    def setUp(self):
        super(TestAccessRights, self).setUp()
        self.user_partner_manager = self.env.ref('base.user_admin')
        self.user_internal = self.env['res.users'].with_context(tracking_disable=True).create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'user@example.viindoo.com',
            'notification_type': 'email',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        self.employee_size = self.env['res.partner.employee.size'].create({
            'name': 'From 10 to 50'
        })
    
    def test_partner_manager_access_right(self):
        employee_size_test = self.env['res.partner.employee.size'].with_user(self.user_partner_manager).create({
            'name': 'From 10 to 50'
        })
        employee_size_test.with_user(self.user_partner_manager).read()
        employee_size_test.with_user(self.user_partner_manager).write({
            'name': 'From 100 to 500'
        })
        employee_size_test.with_user(self.user_partner_manager).unlink()
        
    def test_internal_user_access_right(self):
        self.employee_size.with_user(self.user_internal).read()
        with self.assertRaises(AccessError):
            self.employee_size.with_user(self.user_internal).write({'name':'From 10 to 100'})
        with self.assertRaises(AccessError):
            self.employee_size.with_user(self.user_internal).unlink()
        with self.assertRaises(AccessError):
            employee_size_test = self.env['res.partner.employee.size'].with_user(self.user_internal).create({
                'name': 'From 10 to 50'
            })
