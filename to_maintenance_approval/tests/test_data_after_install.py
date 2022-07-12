from odoo.tests.common import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestDataAfterInstall(TransactionCase):
    
    def test_data_after_install(self):
        approve_type_maintenance = self.env['approval.request.type'].search([
          ('name', '=', 'Maintenance Approval'),
          ('type', '=', 'maintenance_type'),
          ('validation_type', '=', 'leader')
        ], limit=1)
        self.assertTrue(approve_type_maintenance)
