from unittest.mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrEmployee(TransactionCase):

    def setUp(self):
        super(TestHrEmployee, self).setUp()
        self.dob = fields.Date.to_date('1998-08-21')
        self.dob1 = fields.Date.to_date('2002-06-06')
        self.dob2 = fields.Date.to_date('2000-06-03')
        self.dob3 = fields.Date.to_date('2003-06-14')
        self.dob4 = fields.Date.to_date('2000-05-30')
        self.dob5 = fields.Date.to_date('2001-06-04')
        self.dob6 = fields.Date.to_date('2001-05-26')
        self.dob7 = fields.Date.to_date('2000-06-29')
        self.dob8 = fields.Date.to_date('2001-07-02')
        self.dob9 = fields.Date.to_date('2000-06-17')
        self.dob0 = fields.Date.to_date('2001-07-07')
        
        Employee = self.env['hr.employee'].with_context(tracking_disable=True)
        self.employee1 = Employee.create({'name': 'EmployeeX', 'birthday': self.dob1})
        self.employee2 = Employee.create({'name': 'EmployeeY', 'birthday': self.dob2})
        self.employee3 = Employee.create({'name': 'EmployeeZ', 'birthday': self.dob3})
        self.employee4 = Employee.create({'name': 'EmployeeZ', 'birthday': self.dob4})
        self.employee5 = Employee.create({'name': 'EmployeeZ', 'birthday': self.dob5})
        self.employee6 = Employee.create({'name': 'EmployeeZ', 'birthday': self.dob6})
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

    def test_search_birthday_01(self):
        """
        Trường hợp search theo tuàn này, tuần không nằm giữa 2 tháng
        Input: 
            Tìm kiếm tại ngày: 2022-06-06
            Employeex có ngày sinh tuần này: 2002-06-06
            Employeey có ngày sinh tuần trước: 2000-06-03
            Employeez có ngày sinh tuần tới: 2003-06-14
        Output:
            Lọc ra được nhân viên employeeX có ngày sinh
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'this_week')])
            self.assertTrue(employees & self.employee1 )
            self.assertFalse(employees & (self.employee2 | self.employee3))

    def test_search_birthday_02(self):
        """
        Trường hợp search theo tuàn này, tuần nằm giữa 2 tháng
        Input: 
            Tìm kiếm tại ngày: 2022-06-02
            EmployeeX có ngày sinh tháng 5: 2000-05-30
            EmployeeY có ngày sinh tháng 6: 2001-06-04
            EmployeeZ có ngày sinh tuần tới: 2001-06-06
            EmployeeG có ngày sinh tháng trước: 2001-05-26
        Output:
            Lọc ra được nhân viên employeeX và employeeY
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-02')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'this_week')])
            self.assertTrue(employees & (self.employee4 | self.employee5))
            self.assertFalse(employees & (self.employee1 | self.employee6))
 
    def test_search_birthday_03(self):
        """
        Trường hợp search theo tuần tới
        Input: 
            Tìm kiếm tại ngày: 2022-06-02
            EmployeeX có ngày sinh tuần tới: 2000-06-14
            EmployeeY có ngày sinh tuần này: 2000-06-06
            EmployeeZ có ngày sinh tuần trước: 2000-06-04
        Output:
            Lọc ra được nhân viên employeeX
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'next_week')])
            self.assertTrue(employees & self.employee3)
            self.assertFalse(employees & (self.employee1 | self.employee5))

    def test_search_birthday_04(self):
        """
        Trường hợp search theo tuần trước
        Input: 
            Tìm kiếm tại ngày: 2022-06-02
            EmployeeX có ngày sinh tuần tới: 2000-06-14
            EmployeeY có ngày sinh tuần này: 2000-06-06
            EmployeeZ có ngày sinh tuần trước: 2000-06-04
        Output:
            Lọc ra được nhân viên employeeZ
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'last_week')])
            self.assertTrue(employees & self.employee5)
            self.assertFalse(employees & (self.employee3 | self.employee1))

    def test_search_birthday_05(self):
        """
        Trường hợp search theo ngày sinh không ở trong tuần hiện tại
        Input: 
            Tìm kiếm tại ngày: 2022-06-02
            EmployeeY có ngày sinh: 2000-06-06
            EmployeeX có ngày sinh: 2000-05-30
        Output:
            Lọc ra được nhân viên employeeX
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '!=', 'this_week')])
            self.assertTrue(employees & self.employee4)
            self.assertFalse(employees & self.employee1)

    def test_search_birthday_06(self):
        """
        Trường hợp ngày sinh không được thiết lập
        Input: 
            Tìm kiếm tại ngày: 2022-06-02
            EmployeeX có ngày sinh: không tạo ngày sinh
            EmployeeY có ngày sinh: 2000-06-06
        Output:
            Lọc ra được nhân viên employeeX
        """
        employeeX = self.env['hr.employee'].create({'name': 'EmployeeX'})
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', False)])
            self.assertTrue(employees & employeeX)
            self.assertFalse(employees & self.employee1)

    def test_search_birthday_07(self):
        """
        Trường hợp ngày sinh được thiết lập
        Input: 
            Tìm kiếm tại ngày: 2022-06-02
            EmployeeX có ngày sinh: không tạo ngày sinh
            EmployeeY có ngày sinh: 2000-06-06
        Output:
            Lọc ra được nhân viên employeeY
        """
        employeeX = self.env['hr.employee'].create({'name': 'EmployeeX'})
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '!=', False)])
            self.assertTrue(employees & self.employee1)
            self.assertFalse(employees & employeeX)

    def test_search_birthday_08(self):
        """
        Trường hợp search theo tuần trước, tuần không nằm giữa 2 tháng
        Input: 
            Tìm kiếm tại ngày: 2022-06-16
            EmployeeX có ngày sinh: 2022-06-06
            EmployeeY có ngày sinh: 2022-06-17
        Output:
            Lọc ra được nhân viên employeeX
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-16')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'last_week')])

            self.assertTrue(employees & self.employee1)
            self.assertFalse(employees & self.employee3)

    def test_search_birthday_09(self):
        """
        Trường hợp search theo tuàn trước, tuần nằm giữa 2 tháng
        Input: 
            Tìm kiếm tại ngày: 2022-06-06
            EmployeeX có ngày sinh: 2000-05-30
            EmployeeY có ngày sinh: 2001-06-04
            EmployeeZ có ngày sinh: 2001-06-14
        Output:
            Lọc ra được nhân viên employeeX và employeeY
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'last_week')])
            self.assertTrue(employees & (self.employee4 | self.employee5))
            self.assertFalse(employees & self.employee3)

    def test_search_birthday_10(self):
        """
        Trường hợp search theo tuàn tới, tuần không nằm giữa 2 tháng
        Input: 
            Tìm kiếm tại ngày: 2022-06-06
            EmployeeX có ngày sinh: 2022-06-14
            EmployeeY có ngày sinh: 2022-06-06
            EmployeeZ có ngày sinh: 2022-06-03
        Output:
            Lọc ra được nhân viên employeeX
        """
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-06')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'next_week')])
            self.assertTrue(employees & self.employee3)
            self.assertFalse(employees & (self.employee2 | self.employee1))

    def test_search_birthday_11(self):
        """
        Trường hợp search theo tuàn tới, tuần nằm giữa 2 tháng
        Input: 
            Tìm kiếm tại ngày: 2022-06-24
            EmployeeX có ngày sinh: 2000-06-29
            EmployeeY có ngày sinh: 2001-07-02
            EmployeeZ có ngày sinh: 2000-06-17
            EmployeeG có ngày sinh: 2001-07-07
            
        Output:
            Lọc ra được nhân viên employeeX và employeeY
        """
        employeeX = self.env['hr.employee'].create({'name': 'EmployeeX', 'birthday': self.dob7})
        employeeY = self.env['hr.employee'].create({'name': 'EmployeeY', 'birthday': self.dob8})
        employeeZ = self.env['hr.employee'].create({'name': 'EmployeeZ', 'birthday': self.dob9})
        employeeG = self.env['hr.employee'].create({'name': 'EmployeeG', 'birthday': self.dob0})
        with patch.object(fields.Date, 'today', lambda: fields.Date.to_date('2022-06-24')):
            employees = self.env['hr.employee'].search([('birthday_by_week', '=', 'next_week')])
            self.assertTrue(employees & (employeeX | employeeY))
            self.assertFalse(employees & (employeeZ | employeeG))
