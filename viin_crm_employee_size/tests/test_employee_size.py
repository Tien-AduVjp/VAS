from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestEmployeeSize(TransactionCase):

    def setUp(self):
        super(TestEmployeeSize, self).setUp()
        self.employee_size_10_to_50 = self.env['res.partner.employee.size'].create({
            'name':'From 10 to 50'
        })
        self.lead_demo = self.env['crm.lead'].create({
            'name': 'Lead demo'
            })

    def test_choose_employee_size(self):
        """
        Test: Choose the employee size for the lead
        """
        # Test
        self.lead_demo.write({
            'employee_size_id': self.employee_size_10_to_50.id,
        })
        self.assertEqual(self.lead_demo.employee_size_id, self.employee_size_10_to_50, 'Employee size is incorrect')
