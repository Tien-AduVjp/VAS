from odoo.tests import tagged

from .test_tvtma_hr_savepoint import HrTestEmployeeCommon


@tagged('post_install', '-at_install')
class TestHremployee(HrTestEmployeeCommon):
    
    def test_applicant_link_employee(self):
        self.assertTrue(self.employee_a.hr_applicant_ids, "The applicant not link to employee.")
        
    def test_create_employee_not_link_applicant(self):
        employee_b = self.env['hr.employee'].create({
            'name': 'Employee A'
            })
        self.assertFalse(employee_b.hr_applicant_ids, "The applicant link to employee.")
        
    def test_change_state_applicant(self):
        
        self.applicant_a.archive_applicant()
        self.assertFalse(self.employee_a.hr_applicant_ids, "The applicant link to employee.")
        
        self.applicant_a.reset_applicant()
        self.assertTrue(self.employee_a.hr_applicant_ids, "The applicant not link to employee.")
        
    def test_duplicate_employee(self):
        employee_c = self.employee_a.copy()
        self.assertFalse(employee_c.hr_applicant_ids, "The employee not link to applicant.")
    
    def test_input_vat(self):
        # Test change vat on employee
        self.employee_a.write({'vat': 'ATU12345675'})
        partner = self.employee_a.address_home_id
        self.assertTrue(self.employee_a.vat == partner.vat, "The change Vat on employee does not update for partner.")
        self.assertTrue(self.employee_a.vat, 'ATU12345675')
        # Test change vat on partner
        partner.write({'vat': '0477472701'})
        self.assertTrue(self.employee_a.vat == partner.vat, "The change Vat on partner does not update for employee.")
        self.assertTrue(self.employee_a.vat, '0477472701')
