from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrEmployee(TransactionCase):

    def setUp(self):
        super(TestHrEmployee, self).setUp()
        self.dob = fields.Date.to_date('1998-08-21')
        self.employee = self.env['hr.employee'].create({'name': 'John Employee'})
        self.partner = self.env['res.partner'].create({'name': 'John Employee'})

    # TC06
    def test_compute_birthday(self):
        self.employee.write({'birthday': self.dob})
        self.assertEqual(self.employee.birthday, self.dob)
        self.assertEqual(self.employee.dyob, self.dob.day)
        self.assertEqual(self.employee.mob, self.dob.month)
        self.assertEqual(self.employee.yob, self.dob.year)

    # TC07
    def test_compute_empty_birthday(self):
        self.assertEqual(self.employee.birthday, False)
        self.assertEqual(self.employee.dyob, 0)
        self.assertEqual(self.employee.mob, 0)
        self.assertEqual(self.employee.yob, 0)

    # TC08
    def test_get_birthday(self):
        self.employee.write({'address_home_id': self.partner.id})
        self.partner.write({'dob': self.dob})
        self.assertEqual(self.partner.dob, self.employee.birthday)
        self.assertEqual(self.dob, self.employee.birthday)
        
        self.partner.write({'dob': False})
        self.assertEqual(self.dob, self.employee.birthday)
        
        self.employee.write({'address_home_id': False})
        self.assertEqual(self.dob, self.employee.birthday)

    # TC09
    def test_set_birthday(self):
        self.employee.write({'birthday': self.dob, 'address_home_id': self.partner.id})
        # Employee birthday does should match with birthday from address
        self.assertEqual(self.partner.dob, self.employee.birthday)
