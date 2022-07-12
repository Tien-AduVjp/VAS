from odoo.tests.common import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestDataAfterInstall(TransactionCase):

    def test_data_after_install(self):
        approve_type_generic = self.env['approval.request.type'].search([
          ('name', '=', 'Timesheet'),
          ('type', '=', 'timesheets'),
        ], limit=1)
        self.assertTrue(approve_type_generic)
