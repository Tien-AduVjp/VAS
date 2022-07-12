from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.tests.common import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        cls.current_year = fields.Date.today().year
        #Employee
        cls.employee_admin = cls.env.ref('hr.employee_admin')
        cls.employee_demo = cls.env.ref('hr.employee_qdp')
        cls.employee_1 = cls.env.ref('hr.employee_stw')

        # Contract
        cls.contract_admin = cls.env.ref('hr_contract.hr_contract_admin')
        cls.contract_admin.write({'pay_per_meal': 30000})
        if cls.contract_admin.state == 'draft':
            cls.contract_admin.action_start_contract() #Open contract

        cls.contract_employee_demo = cls.env.ref('hr_contract.hr_contract_qdp')
        cls.contract_employee_demo.write({
            'pay_per_meal': 30000,
            'date_start': fields.Date.to_date('%s-01-01'%cls.current_year)
        })
        cls.contract_employee_1 = cls.env.ref('hr_contract.hr_contract_stw')
        cls.contract_employee_1.write({
            'pay_per_meal': 30000,
            'date_start': fields.Date.to_date('%s-01-01'%cls.current_year)
        })

        # Meal type
        cls.meal_type_1 = cls.env.ref('to_hr_meal.hr_meal_type_lunch_for_everyone')

        #Meal Orders
        cls.meal_order_1 = cls.env['hr.meal.order'].create({
            'meal_type_id': cls.meal_type_1.id,
            'scheduled_hour': 12
        })
        cls.meal_order_2 = cls.env['hr.meal.order'].create({
            'meal_type_id': cls.meal_type_1.id,
            'scheduled_date': date.today() + relativedelta(months=1),
            'scheduled_hour': 12
        })
        # Meal line data
        cls.meal_line_admin_data = {
            'employee_id': cls.employee_admin.id,
            'quantity': 1,
            'price': 35000,
            'meal_type_id': cls.meal_type_1.id
        }

        #Salary structure
        cls.salary_structure = cls.env['hr.payroll.structure'].search([('code', '=', 'BASE')], limit=1)

        #Salary Cycle
        cls.salary_cycle_default = cls.env.ref('to_hr_payroll.hr_salary_cycle_default')

        #Payslip data
        cls.payslip_admin_data = {
            'employee_id': cls.employee_admin.id,
            'contract_id' : cls.contract_admin.id,
            'struct_id': cls.salary_structure.id,
            'salary_cycle_id': cls.salary_cycle_default.id,
            'company_id': cls.env.company.id
        }

        cls.payslip_admin = cls.env['hr.payslip'].create(cls.payslip_admin_data)
