from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from .common import Common


@tagged('access_rights', '-at_install', 'post_install')
class TestAccessRights(Common):
    #TC1
    def test_internal_user_access_rights(self):
        # Internal Users can read the document template
        self.document_template.with_user(self.internal_user).read()
        # Internal Users can create the document template
        document_template = self.env['document.template'].with_user(self.internal_user).create({
            'name': 'Demo',
            'model_id': self.model_id.id
        })
        # Internal Users can write the document template
        self.document_template.with_user(self.internal_user).write({'name': 'Demo Write'})
        # Internal Users cannot unlink the document template
        with self.assertRaises(AccessError):
            self.document_template.with_user(self.internal_user).unlink()
    #TC2
    def test_settings_user_access_rights(self):
        # Settings Users can read the document template
        self.document_template.with_user(self.settings_user).read()
        # Settings Users can create the document template
        document_template = self.env['document.template'].with_user(self.settings_user).create({
            'name': 'Demo',
            'model_id': self.model_id.id
        })
        # Settings Users can write the document template
        self.document_template.with_user(self.settings_user).write({'name': 'Demo Write'})
        # Settings Users can unlink the document template
        self.document_template.with_user(self.settings_user).unlink()
