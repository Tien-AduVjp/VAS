from psycopg2 import IntegrityError

from odoo.tools import mute_logger
from odoo.tests import TransactionCase, tagged
from odoo.tests.common import Form


@tagged('post_install', '-at_install')
class TestEmployeeSize(TransactionCase):

    def setUp(self):
        super(TestEmployeeSize, self).setUp()
        self.employee_size_10_to_50 = self.env['res.partner.employee.size'].create({
            'name':'From 10 to 50'
        })
        self.employee_size_100_to_500 = self.env['res.partner.employee.size'].create({
            'name':'From 100 to 500'
        })
        self.contact_a = self.env['res.partner'].create({
            'name':'Contact A',
            'company_type': 'company',
            'employee_size_id':self.employee_size_10_to_50.id
        })
        self.contact_b = self.env['res.partner'].create({
            'name':'Contact B',
            'company_type': 'person',
        })

    def test_choose_employee_size(self):
        """
        Test1: Choose the employee size for the contact, which is company type
        Test2: In the form view, change company type to individual and don't save, later change individual type to company and check employee size
        """
        # Test1
        self.assertEqual(self.contact_a.employee_size_id, self.employee_size_10_to_50, "Employee size is incorrect")
        
        # Test2
        contact_a_form = Form(self.contact_a)
        contact_a_form.company_type = 'person'
        contact_a_form.company_type = 'company'
        self.assertEqual(contact_a_form.employee_size_id, self.employee_size_10_to_50, "After change company type, employee size is incorrect")

    def test_change_company_type(self):
        """
        Test1: Change company type to individual, check employee size
        Test2: Change company type to individual and save, later change individual type to company and check employee size
        """
        # Test1
        contact_a_form = Form(self.contact_a)
        contact_a_form.company_type = 'person'
        self.assertNotEqual(contact_a_form.employee_size_id, self.employee_size_10_to_50, "Employee size information is still exists")

        # Test2
        contact_b_form = Form(self.contact_b)
        contact_b_form.company_type = 'company'
        self.assertNotEqual(contact_b_form.employee_size_id, self.employee_size_10_to_50, "Employee size information is still exists")
    
    def test_change_employee_size_contact(self):
        """
        Test1: Change employee size 'From 10 to 50' to 'From 100 to 500'
        Test2: Change employee size is False
        """
        #Test 1
        self.contact_a.write({'employee_size_id': self.employee_size_100_to_500.id})
        self.assertEqual(self.contact_a.employee_size_id.id, self.employee_size_100_to_500.id)
        
        #Test 2
        self.contact_a.write({'employee_size_id': False})
        self.assertFalse(self.contact_a.employee_size_id)
    
    @mute_logger('odoo.sql_db')
    def test_01_remove_employee_size(self):
        # Remove employee size when assigned to a partner 
        with self.assertRaises(IntegrityError):
            self.employee_size_10_to_50.unlink()
    
    def test_02_remove_employee_size(self):
        # Remove employee size when not assigned to a partner
        self.employee_size_100_to_500.unlink()
