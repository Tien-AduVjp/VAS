from odoo.tests import tagged
from odoo.tests import SavepointCase
from odoo import fields


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRights, cls).setUpClass()
        cls.restricted_editor = cls.env['res.users']\
            .with_context({'no_reset_password': True, 'tracking_disable': True})\
            .create({
                'name': 'Restricted Editor',
                'login': 'restricted',
                'groups_id': [(6, 0, [
                    cls.env.ref('base.group_user').id,
                    cls.env.ref('website.group_website_publisher').id
                    ])]
                })
        cls.odoo_version = cls.env['odoo.version'].create({
            'name': '15.1',
            'release_date': fields.Date.today()
        })

    def test_access_odoo_version(self):
        OdooVersion = self.env['odoo.version'].with_user(self.restricted_editor)
        another_odoo_version = self.odoo_version.with_user(self.restricted_editor)
        own_odoo_version = OdooVersion.create({
            'name': '13.1',
            'release_date': fields.Date.today()
        })
        own_odoo_version.read(['name'])
        own_odoo_version.name = '13.2'
        own_odoo_version.unlink()

        another_odoo_version.read(['name'])
        another_odoo_version.name = '15.2'
        another_odoo_version.unlink()
