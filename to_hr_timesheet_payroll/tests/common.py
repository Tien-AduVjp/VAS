from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        # Group
        group_user_internal = cls.env.ref('base.group_user')
        group_user_payroll = cls.env.ref('to_hr_payroll.group_hr_payroll_user')
        #User
        cls.user_payroll = cls.env['res.users'].with_context(tracking_disable=True).create({
            'name': 'User Payroll',
            'login': 'user_payroll',
            'groups_id': [(6, 0, [group_user_internal.id, group_user_payroll.id])],
        })
        #Salary structure
        cls.salary_structure = cls.env['hr.payroll.structure'].search([('code', '=', 'BASE')], limit=1)
        #Job Position
        cls.job_payroll_timesheet_enable = cls.env['hr.job'].create({
            'name' : 'Job Payroll Timesheet Enable',
            'payroll_timesheet_enabled': True
        })
        cls.job_payroll_timesheet_disable = cls.env['hr.job'].create({
            'name' : 'Job Payroll Timesheet Disable',
            'payroll_timesheet_enabled': False
        })
        
        #Employee have open contract
        cls.employee_1 = cls.env.ref('hr.employee_han')
        cls.employee_2 = cls.env.ref('hr.employee_stw')
        #Employee have draft contract
        cls.employee_3 = cls.env.ref('hr.employee_qdp')
        #Employees to test the case of multiple contracts in a pay cycle
        cls.employee_4 = cls.env.ref('hr.employee_mit')
        
        # Contract Open
        cls.contract_employee_1 = cls.env.ref('hr_contract.hr_contract_han')
        cls.contract_employee_2 = cls.env.ref('hr_contract.hr_contract_stw')
        # Contract Draft
        cls.contract_employee_3 = cls.env.ref('hr_contract.hr_contract_qdp')
        #set default date contract
        cls.contract_employee_1.date_start = '2021-01-01'
        cls.contract_employee_2.date_start = '2021-01-01'
        cls.contract_employee_3.date_start = '2021-01-01'
        
        #Contract : Test the case of multiple contracts in a pay cycle
        cls.contract_1_employee_4 = cls.env.ref('hr_contract.hr_contract_mit')
        cls.contract_1_employee_4.write({
            'date_start': '2021-10-01',
            'date_end': '2021-10-22',
            'wage': 5000
        })
        cls.contract_2_employee_4 = cls.env['hr.contract'].create({
            'name': 'Employee 4',
            'employee_id': cls.employee_4.id,
            'company_id': cls.env.company.id,
            'struct_id': cls.salary_structure.id,
            'date_start': '2021-10-23',
            'wage': 10000,
        })
        
        #Project
        cls.project_1 = cls.env.ref('project.project_project_2')
        
        #Timesheet Employee 1
        cls.timesheet_1 = cls.env['account.analytic.line'].create({
            'date': '2021-10-10',
            'name': 'Timesheet 1 Employee 1',
            'project_id': cls.project_1.id,
            'employee_id': cls.employee_1.id,
            'unit_amount': 1,
        })
        cls.timesheet_2 = cls.env['account.analytic.line'].create({
            'date': '2021-10-31',
            'name': 'Timesheet 2 Employee 1',
            'project_id': cls.project_1.id,
            'employee_id': cls.employee_1.id,
            'unit_amount': 1,
        })
        
        #Timesheet Employee 2
        cls.timesheet_3 = cls.env['account.analytic.line'].create({
            'date': '2021-10-01',
            'name': 'Timesheet 1 Employee 2',
            'project_id': cls.project_1.id,
            'employee_id': cls.employee_2.id,
            'unit_amount': 1,
        })
        
        #Timesheet Employee 4
        cls.timesheet_4 = cls.env['account.analytic.line'].create({
            'date': '2021-10-24',
            'name': 'Timesheet 1 Employee 4',
            'project_id': cls.project_1.id,
            'employee_id': cls.employee_4.id,
            'unit_amount': 8,
        })
        cls.timesheet_5 = cls.env['account.analytic.line'].create({
            'date': '2021-10-25',
            'name': 'Timesheet 2 Employee 4',
            'project_id': cls.project_1.id,
            'employee_id': cls.employee_4.id,
            'unit_amount': 8,
        })
        
        #Payslip
        #Payslip Employee 1
        cls.payslip_employee_1 = cls.env['hr.payslip'].create({
            'employee_id': cls.employee_1.id,
            'contract_id' : cls.employee_1.contract_id.id,
            'struct_id': cls.salary_structure.id,
            'date_from': '2021-10-01',
            'date_to': '2021-10-22',
            'company_id': cls.env.company.id
        })
