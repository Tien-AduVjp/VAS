from odoo.tests import tagged
from odoo.tools.misc import mute_logger
from odoo.exceptions import ValidationError

try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    import psycopg2
    UniqueViolation = psycopg2.IntegrityError

from .test_to_hr_employee_relative_common import TestRelativeCommon

@tagged('post_install','-at_install')
class TestRelativeFunction(TestRelativeCommon):
# Test functional
    # Case 1: Check relations duplicating
    @mute_logger('odoo.sql_db')
    def test_01_relation_duplicate(self): 
        with self.assertRaises(UniqueViolation):
            self.relative_a = self.env['hr.employee.relative'].create({
                'employee_id': self.employee_a.id,
                'contact_id': self.father.id,
                'type': 'friend',
                })
    # Case 2: Check 2 employees have the same relation       
    def test_02_relation_employee(self):
        employee = (self.employee_a | self.employee_b).ids
        employees_relative = self.env['hr.employee'].search([('relative_ids','!=', False)]).ids
        employees_not_relative = self.env['hr.employee'].search([('relative_ids','=', False)]).ids
        partner_relative = self.env['res.partner'].search([('is_employee_relative','!=', False)]).ids
        
        check_employee_in_employees_relative = all(x in employees_relative for x in employee)
        check_employee_in_employees_not_relative = any(x in employees_not_relative for x in employee)
        relatives = self.father.relative_employee_ids.ids
        
        self.assertEqual(
            check_employee_in_employees_relative, True, 
            'the {} not in to {}'.format(employee, employees_relative)
            )
        self.assertEqual(
            not check_employee_in_employees_not_relative, True, 
            'the {} not in to {}'.format(employee, employees_not_relative)
            )
        self.assertEqual(
            employee, relatives, 
            'the {} not in to {}'.format(employee, relatives)
            )
        self.assertEqual(
            self.father.id in partner_relative, True, 
            'the {} not in to {}'.format(self.father.id, partner_relative)
            )
        
    # Case 3: Check unlink a relation
    def test_03_unlink_relation(self):
        self.relative_father_a.unlink()
        self.relative_mother_a.unlink()
        self.relative_wife_a.unlink()
        employees_not_relative = self.env['hr.employee'].search([('relative_ids','=', False)]).ids
        partner_not_relative = self.env['res.partner'].search([('is_employee_relative','=', False)]).ids
        
        check_employee_in_employees_not_relative = self.employee_a.id in employees_not_relative
        
        self.assertEqual(
            check_employee_in_employees_not_relative, True, 
            'the {} not in to {}'.format(self.employee_b, employees_not_relative)
            )
        self.assertEqual(
            self.wife_a.id in partner_not_relative, True, 
            'the {} not in to {}'.format(self.wife_a.id, partner_not_relative)
            )
        

