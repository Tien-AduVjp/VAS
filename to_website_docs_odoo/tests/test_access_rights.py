from odoo import fields
from odoo.tests import tagged
from .common import TestDocsCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestOdooVersionAccessRights(TestDocsCommon):

    def test_docs_editor_crud_odoo_version(self):
        # test odoo.version crud with doc editor
        odoo_version = self.env['odoo.version'].with_user(self.editor_user).create({
            'name': '19.0',
            'release_date': fields.Date.today()
        })
        self.assertEqual(odoo_version.name, '19.0', 'Test read odoo version failed')
        odoo_version.name = '49.0'
        self.assertEqual(odoo_version.name, '49.0', 'Test write odoo version failed')
        self.assertTrue(odoo_version.unlink(), 'Test delete odoo version failed')
