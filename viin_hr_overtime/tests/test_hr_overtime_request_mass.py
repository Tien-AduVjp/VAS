from datetime import date, timedelta
from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.exceptions import UserError, AccessError
from odoo.tools import mute_logger

from .common import  Common


@tagged('post_install', '-at_install')
class TestHrOvertimeRequestMass(Common):

    #-----------------------------------------------------------Test Form-----------------------------------------------------------#

    def test_01_compute_employee_ids(self):
        """
            Case: Test compute employees when selected mode is "department".
            Expect: Show all employees belong to the selected departments.
        """
        self.ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id
        })
        self.assertEqual(self.ot_request_mass.mode, 'department')
        self.ot_request_mass.department_ids = [(6, 0, [self.env.ref('hr.job_consultant').id, self.env.ref('hr.job_developer').id])]
        department_employees = self.env['hr.employee'].search([('department_id', 'in', self.ot_request_mass.department_ids.ids)])
        self.assertEqual(self.ot_request_mass.employee_ids, department_employees)

    def test_03_compute_employee_ids(self):
        """
            Case: Test compute employees when selected mode is "employee" and user make plan in admin group.
            Expect: Show all employees
        """
        self.env.user = self.user_01
        self.env.user.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_admin').id, 0)]
        self.ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'employee'
        })
        employees = self.env['hr.employee'].search([])
        self.assertEqual(self.ot_request_mass.employee_ids, employees)

    def test_03a_compute_employee_ids(self):
        """
            Case: Test compute employees when selected mode is "employee" and user make plan in officer group.
            Expect: Show all employees
        """
        self.env.user = self.user_01
        self.env.user.groups_id = [(4, self.env.ref('viin_hr_overtime.group_overtime_officer').id, 0)]
        self.ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'employee'
        })
        employees = self.env['hr.employee'].search([])
        self.assertEqual(self.ot_request_mass.employee_ids, employees)

    def test_04_compute_employee_ids(self):
        """
            Case: Test compute employees when selected mode is "employee" and user make plan in team approval group.
            Expect: Show all subordinate employees and user make plan
        """
        self.user_01.groups_id = self.env.ref('viin_hr_overtime.group_overtime_team_approval')
        self.user_02.employee_id.parent_id = self.user_01.employee_id
        self.user_03.employee_id.parent_id = self.user_01.employee_id
        self.ot_request_mass = self.env['hr.overtime.request.mass'].with_user(self.user_01).create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'employee'
        })
        self.assertEqual(self.ot_request_mass.employee_ids, self.user_01.employee_id.subordinate_ids | self.user_01.employee_id)

    def test_05_compute_employee_ids(self):
        """
            Case: Test compute employees when selected mode is "department" then add more employee in others departments.
            Expect: Show all employees in selected departments and employees, whose were added.
        """
        self.ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'department_ids':[(6, 0, [self.env.ref('hr.job_consultant').id])]
        })

        employees = self.ot_request_mass.employee_ids
        self.ot_request_mass.employee_ids = [(4, self.employee_01.id, 0)]
        self.assertEqual(self.ot_request_mass.employee_ids, employees + self.employee_01)

    def test_06_compute_employee_ids(self):
        """
            Case: Test compute employees when selected mode is "department", then remove some employees.
            Expect: Show all employees in selected departments with out employees were removed,.
        """
        self.ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'department_ids':[(6, 0, [self.env.ref('hr.job_consultant').id])]
        })
        employees = self.ot_request_mass.employee_ids
        self.ot_request_mass.employee_ids = [(3, self.env.ref('hr.employee_jgo').id, 0)]
        self.assertEqual(self.ot_request_mass.employee_ids, employees - self.env.ref('hr.employee_jgo'))

    def test_07_compute_employee_ids(self):
        """
            Case: Test compute employees in multiple company and selected mode is "company".
            Expected: Show all employees in selected company (not depend by department).

        """
        self.user_02.employee_id.company_id = self.company_01.id
        self.user_03.employee_id.company_id = self.company_01.id
        self.ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'department_ids':[(6, 0, [self.env.ref('hr.job_consultant').id])],
            'company_ids':[(6, 0, [self.company_01.id])],
            'mode':'company'
        })
        self.assertEqual(self.ot_request_mass.employee_ids, self.user_03.employee_id | self.user_02.employee_id)

    #-----------------------------------------------------------Test Functional-----------------------------------------------------------#

    def test_01_generate_ot_mass_schedule(self):
        """
            Case: Test generate overtime mass schedule.
            Expect: Creation successfully with overtime plan for each employee satisfy mass schedule line.
        """
        ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'department',
            'department_ids':[(6, 0, [self.env.ref('hr.dep_rd').id])],
            'line_ids':[(0, 0, {
                    'date':self.next_monday,
                    'time_start':1.5,
                    'time_end':23.5
                })]
        })
        plans = ot_request_mass._generate_overtime_plans()
        self.assertEqual(len(plans), len(ot_request_mass.employee_ids) * len(ot_request_mass.line_ids))
        for p in plans:
            overtime_rule = self.env['hr.overtime.rule'].search([
                ('weekday', '=', str(self.next_monday.weekday())),
                ('company_id', '=', p.employee_id.company_id.id),
                ('holiday', '=', False)
                ])
            ot_lines = self._calculate_overtime_line(p, overtime_rule, p.employee_id.contract_id)
            self.assertEqual(len(ot_lines), len(p.line_ids))
            for pos, l in enumerate(p.line_ids):
                (ot_rule_id, (start_time, end_time)) = ot_lines[pos]
                self.assertEqual(l.hr_overtime_rule_id.id, ot_rule_id)
                self.assertEqual(round(l.planned_hours,2), round(end_time - start_time,2))

    @mute_logger('odoo.sql_db')
    def test_02_generate_ot_mass_schedule(self):
        """
            Case: Test generate overtime mass schedule with time end is smaller than time start.
            Expect: Show User Error
        """
        with self.assertRaises(IntegrityError):
            ot_request_mass = self.env['hr.overtime.request.mass'].create({
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
                'mode':'department',
                'department_ids':[(6, 0, [self.env.ref('hr.dep_rd').id])],
                'line_ids':[(0, 0, {
                        'date':self.next_monday,
                        'time_start':18.5,
                        'time_end':17.5
                    })]
                })
            ot_request_mass._generate_overtime_plans()

    def test_03_generate_ot_mass_schedule(self):
        """
            Case: Test generate overtime plan mass schedule in case period time of lines is overlap.
            Expect:Creation is not successfully, show user error.
        """
        with self.assertRaises(UserError):
            ot_request_mass = self.env['hr.overtime.request.mass'].create({
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
                'mode':'department',
                'department_ids':[(6, 0, [self.env.ref('hr.dep_rd').id])],
                'line_ids':[
                    (0, 0, {
                        'date':self.next_monday,
                        'time_start':17.0,
                        'time_end':18.5
                    }),
                    (0, 0, {
                        'date':self.next_monday,
                        'time_start':17.5,
                        'time_end':18.5
                    })
                ]
            })
            ot_request_mass._generate_overtime_plans()

    def test_04_generate_ot_mass_schedule(self):
        """
            Case: Test generate overtime plan mass schedule in case period time is overlap existed plan.
            Expect: Creation is not successfully, show user error
        """
        self.user_01 = self.env.ref('hr.dep_rd').id
        self.overtime_plan_emp_01.update({
            'date':self.next_monday,
            'time_end':19.0,
            'time_start':17.0,
        })
        with self.assertRaises(UserError):
            ot_request_mass = self.env['hr.overtime.request.mass'].create({
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
                'mode':'department',
                'department_ids':[(6, 0, [self.env.ref('hr.dep_rd').id])],
                'line_ids':[(0, 0, {
                        'date':self.next_monday,
                        'time_start':17.5,
                        'time_end':19.0
                    })]
            })
            ot_request_mass._generate_overtime_plans()

    def test_05_generate_ot_mass_schedule(self):
        """
            Case: Test generate overtime plan mass schedule in case contract of user expired.
            Expect: Can create overtime plan but not attach contract and overtime line is empty.
        """
        self.contracts_emp_01.update({
            'date_start': date.today() - timedelta(days=365),
            'date_end': date.today() - timedelta(days=2)
        })
        ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'employee',
            'employee_ids':[(6, 0, [self.employee_01.id])],
            'line_ids':[(0, 0, {
                    'date':self.next_monday,
                    'time_start':1.5,
                    'time_end':23.5
                })]
        })
        plans = ot_request_mass._generate_overtime_plans()
        self.assertEqual(len(plans), len(ot_request_mass.employee_ids) * len(ot_request_mass.line_ids))
        self.assertFalse(plans.contract_ids)
        self.assertFalse(plans.line_ids)

    def test_06_generate_ot_mass_schedule(self):
        """
            Case: Test generate overtime plan mass schedule in case overtime line in multiple intervals and multiple overtime rule.
            Expect: Generate exactly overtime plan for each employee with overtime line satisfy mass schedule line.
        """
        self.next_tuesday = self._generate_overtime_plan_date(1)
        self.next_wednesday = self._generate_overtime_plan_date(2)
        self.next_thursday = self._generate_overtime_plan_date(3)
        self.next_friday = self._generate_overtime_plan_date(4)
        self.next_saturday = self._generate_overtime_plan_date(5)
        self.next_sunday = self._generate_overtime_plan_date(6)
        ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'department',
            'department_ids':[(6, 0, [self.env.ref('hr.dep_rd').id])],
            'line_ids':[
                (0, 0, {
                    'date':self.next_monday,
                    'time_start':3.0,
                    'time_end':6.0
                }),
                (0, 0, {
                    'date':self.next_monday,
                    'time_start':6.1,
                    'time_end':13.0
                }),
                (0, 0, {
                    'date':self.next_monday,
                    'time_start':13.1,
                    'time_end':23.9
                }),
                (0, 0, {
                    'date':self.next_tuesday,
                    'time_start':3.0,
                    'time_end':23.5
                }),
                (0, 0, {
                    'date':self.next_wednesday,
                    'time_start':3.0,
                    'time_end':12.0
                }),
                (0, 0, {
                    'date':self.next_wednesday,
                    'time_start':12.0,
                    'time_end':16.0
                }),
                (0, 0, {
                    'date':self.next_thursday,
                    'time_start':13.25,
                    'time_end':22.25
                }),
                (0, 0, {
                    'date':self.next_friday,
                    'time_start':18.2,
                    'time_end':23.5
                }),
                (0, 0, {
                    'date':self.next_saturday,
                    'time_start':14.25,
                    'time_end':19.25
                }),
                (0, 0, {
                    'date':self.next_sunday,
                    'time_start':22.0,
                    'time_end':23.9
                })
            ]
        })
        plans = ot_request_mass._generate_overtime_plans()
        self.assertEqual(len(plans), len(ot_request_mass.employee_ids) * len(ot_request_mass.line_ids))
        for p in plans:
            overtime_rule = self.env['hr.overtime.rule'].search([
                ('weekday', '=', str(p.date.weekday())),
                ('company_id', '=', p.employee_id.company_id.id),
                ('holiday', '=', False)
                ])
            ot_lines = self._calculate_overtime_line(p, overtime_rule, p.employee_id.contract_id)
            self.assertEqual(len(ot_lines), len(p.line_ids))
            for pos, l in enumerate(p.line_ids):
                (ot_rule_id, (start_time, end_time)) = ot_lines[pos]
                self.assertEqual(l.hr_overtime_rule_id.id, ot_rule_id)
                self.assertEqual(round(l.planned_hours, 2), round(end_time - start_time, 2))

    def test_07_generate_ot_mass_schedule(self):
        """
            Test generate overtime plan mass schedule in case employees in multiple company.
            Expect: Generate exactly overtime plan for each user satisfy overtime line.
        """
        self.company_03 = self.env['res.company'].create({
                'name': "Company Testing 03"
            })
        self.user_02.employee_id.company_id = self.company_01.id
        self.user_03.employee_id.company_id = self.company_03.id
        contract_emp_02 = self.contracts_emp_01.copy()
        contract_emp_03 = self.contracts_emp_01.copy()
        contract_emp_02.update({
            'company_id':self.company_01.id,
            'employee_id':self.user_02.employee_id.id,
            'date_start': date.today() + timedelta(days=1),
            'date_end': date.today() + timedelta(days=365)
        })
        contract_emp_03.update({
            'company_id':self.company_03.id,
            'employee_id':self.user_03.employee_id.id,
            'date_start': date.today() + timedelta(days=1),
            'date_end': date.today() + timedelta(days=365)
        })
        contract_emp_02.action_start_contract()
        contract_emp_03.action_start_contract()
        ot_request_mass = self.env['hr.overtime.request.mass'].create({
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id,
            'mode':'company',
            'company_ids':[(6, 0, [self.company_01.id, self.company_03.id])],
            'line_ids':[(0, 0, {
                    'date':self.next_monday,
                    'time_start':1.5,
                    'time_end':23.5
                })]
        })
        plans = ot_request_mass._generate_overtime_plans()
        self.assertEqual(len(plans), len(ot_request_mass.employee_ids) * len(ot_request_mass.line_ids))
        for p in plans:
            overtime_rule = self.env['hr.overtime.rule'].search([
                ('weekday', '=', str(p.date.weekday())),
                ('company_id', '=', p.employee_id.company_id.id),
                ('holiday', '=', False)
                ])

            ot_lines = self._calculate_overtime_line(p, overtime_rule, p.employee_id.contract_id)
            self.assertEqual(len(ot_lines), len(p.line_ids))
            for pos, l in enumerate(p.line_ids):
                (ot_rule_id, (start_time, end_time)) = ot_lines[pos]
                self.assertEqual(l.hr_overtime_rule_id.id, ot_rule_id)
                self.assertEqual(round(l.planned_hours, 2), round(end_time - start_time, 2))
