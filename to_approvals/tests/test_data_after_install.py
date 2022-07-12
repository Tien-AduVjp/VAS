from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestDataAfterInstall(Common):
    
    def test_data_after_install(self):
        approve_type_generic = self.env['approval.request.type'].search([
          ('name', '=', 'General Approval'),
          ('type', '=', 'generic'),
          ('validation_type', '=', 'leader')
        ], limit=1)
        self.assertTrue(approve_type_generic)
