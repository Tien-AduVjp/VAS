from odoo import fields
from odoo.tools import relativedelta
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestHrProjectTimeSheetTimeOffPayroll(TransactionCase):

    def setUp(self):
        super(TestHrProjectTimeSheetTimeOffPayroll, self).setUp()
        self.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        self.env = self.env(context=dict(self.no_mailthread_features_ctx, **self.env.context))
        self.user = self.env.ref('base.user_demo')
        # hardcoded today as 15 of the month to ensure later tests run within a single month
        today = fields.Date.today() - relativedelta(day=15)
        contract = self.user.employee_id.contract_ids[-1:]
        contract.write({
            'date_start': fields.Date.start_of(today, 'year') - relativedelta(years=1),
            'date_end': False,
            'state':'open'
            })
        start_of_week = fields.Date.start_of(today, 'week')
        self.paid_time_off_1 = self.env['hr.leave'].create({
            'name': 'Test',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_cl').id,
            'date_from': start_of_week.strftime('%Y-%m-%d 08:00:00'),
            'date_to': start_of_week.strftime('%Y-%m-%d 17:00:00'),
            'timesheet_project_id': self.env.ref('project.project_project_1').id,
            'timesheet_task_id': self.env.ref('project.project_task_7').id,
            'number_of_days': 1,
        })

        self.paid_time_off_2 = self.env['hr.leave'].create({
            'name': 'Test_2',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_cl').id,
            'date_from': (start_of_week + relativedelta(days=1)).strftime('%Y-%m-%d 08:00:00'),
            'date_to': (start_of_week + relativedelta(days=1)).strftime('%Y-%m-%d 17:00:00'),
            'timesheet_project_id': self.env.ref('project.project_project_1').id,
            'timesheet_task_id': self.env.ref('project.project_task_6').id,
            'number_of_days': 1,
        })
        self.paid_time_off_3 = self.env['hr.leave'].create({
            'name': 'Test_3',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_cl').id,
            'date_from': (start_of_week + relativedelta(days=2)).strftime('%Y-%m-%d 08:00:00'),
            'date_to': (start_of_week + relativedelta(days=2)).strftime('%Y-%m-%d 17:00:00'),
            'timesheet_project_id': self.env.ref('project.project_project_2').id,
            'timesheet_task_id': self.env.ref('project.project_task_12').id,
            'number_of_days': 1,
        })
        
        self.unpaid_time_off = self.env['hr.leave'].create({
            'name': 'Test_2',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
            'date_from': (start_of_week + relativedelta(days=3)).strftime('%Y-%m-%d 08:00:00'),
            'date_to': (start_of_week + relativedelta(days=3)).strftime('%Y-%m-%d 17:00:00'),
            'timesheet_project_id': self.env.ref('project.project_project_1').id,
            'timesheet_task_id': self.env.ref('project.project_task_6').id,
            'number_of_days': 1,
        })

        (
            self.paid_time_off_1 + self.paid_time_off_2 + self.paid_time_off_3 + self.unpaid_time_off
            ).action_validate()
        self.payslip = self.env['hr.payslip'].create({
            'employee_id': self.user.employee_id.id,
            'contract_id': self.user.employee_id.contract_ids[0].id,
            'company_id': self.env.company.id,
            'date_from': fields.Date.start_of(today, 'month'),
            'date_to': fields.Date.end_of(today, 'month'),
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
        })

    def test_hr_project_timesheet_timeoff_payroll(self):
        self.assertEqual(len(self.paid_time_off_1.timesheet_ids), 1)
        self.assertEqual(len(self.paid_time_off_2.timesheet_ids), 1)
        self.assertEqual(len(self.paid_time_off_3.timesheet_ids), 1)
        self.assertNotIn(self.paid_time_off_1.timesheet_ids.id, self.payslip.timesheet_line_ids.ids,
                         "to_hr_project_timesheet_timeoff_payroll: Error exclude timesheet records that represent time off")
        self.assertNotIn(self.paid_time_off_2.timesheet_ids.id, self.payslip.timesheet_line_ids.ids,
                         "to_hr_project_timesheet_timeoff_payroll: Error exclude timesheet records that represent time off")
        self.assertNotIn(self.paid_time_off_3.timesheet_ids.id, self.payslip.timesheet_line_ids.ids,
                         "to_hr_project_timesheet_timeoff_payroll: Error exclude timesheet records that represent time off")
