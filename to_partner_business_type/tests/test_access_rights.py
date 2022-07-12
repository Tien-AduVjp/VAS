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
        self.business_type = self.env['res.partner.business.type'].create({
            'name': 'Joint Stock Company'
        })

    def test_partner_manager_access_right(self):
        business_type_test = self.env['res.partner.business.type'].with_user(self.user_partner_manager).create({
            'name': 'Joint Stock Company Test 1'
        })
        business_type_test.with_user(self.user_partner_manager).read()
        business_type_test.with_user(self.user_partner_manager).write({
            'name': 'Joint Stock Company Test 2'
        })
        business_type_test.with_user(self.user_partner_manager).unlink()

    def test_internal_user_access_right(self):
        self.business_type.with_user(self.user_internal).read()
        with self.assertRaises(AccessError):
            self.business_type.with_user(self.user_internal).write({'name':'Joint Stock Company Test'})
        with self.assertRaises(AccessError):
            self.business_type.with_user(self.user_internal).unlink()
        with self.assertRaises(AccessError):
            business_type_test = self.env['res.partner.business.type'].with_user(self.user_internal).create({
                'name': 'Joint Stock Company Test'
            })
