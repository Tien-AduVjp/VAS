from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrEmployee(TransactionCase):

    def setUp(self):
        super(TestHrEmployee, self).setUp()
        self.dob = fields.Date.from_string('1998-08-21')
        self.employee = self.env['hr.employee'].create({'name': 'John Employee'})
        self.partner = self.env['res.partner'].create({'name': 'John Employee'})
        self.employee_public = self.env['hr.employee.public'].browse(self.employee.id)

    # TC06
    def test_compute_birthday(self):
        self.employee.write({'birthday': self.dob})
        self.employee.flush()
        self.employee_public._compute_yy_mm_of_birth()

        result = {
            'birthday': self.employee_public.birthday,
            'dyob': self.employee_public.dyob,
            'mob': self.employee_public.mob,
            'yob': self.employee_public.yob,
        }
        check_vals = {
            'birthday': self.dob,
            'dyob': self.dob.day,
            'mob': self.dob.month,
            'yob': self.dob.year,
        }
        self.assertEqual(check_vals, result, "Wrong birthday values")

    # TC07
    def test_compute_empty_birthday(self):
        self.employee_public._compute_yy_mm_of_birth()

        result = {
            'birthday': self.employee_public.birthday,
            'dyob': self.employee_public.dyob,
            'mob': self.employee_public.mob,
            'yob': self.employee_public.yob,
        }
        check_vals = {
            'birthday': False,
            'dyob': 0,
            'mob': 0,
            'yob': 0,
        }
        self.assertEqual(check_vals, result, "Wrong empty birthday values")

    # TC08
    def test_get_birthday(self):
        self.partner.write({'dob': self.dob})
        self.employee.write({'address_id': self.partner.id})
        self.employee.flush()
        self.employee_public._get_birthday()

        # Check if employee birthday is same as on partner
        self.assertEqual(self.partner.dob, self.employee_public.birthday, "Birthday from address does not match with employee birthday")

    # TC09
    def test_set_birthday(self):
        self.employee.write({'birthday': self.dob, 'address_id': self.partner.id})
        self.employee.flush()
        self.employee_public._set_birthday()

        # Check if partner birthday is same as on employee
        self.assertEqual(self.partner.dob, self.employee_public.birthday, "Employee birthday does not match with birthday from address")
