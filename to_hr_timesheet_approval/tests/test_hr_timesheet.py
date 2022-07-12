from datetime import date, timedelta

from odoo.tests.common import tagged

from .common import CommonTimesheetApproval


@tagged('-at_install', 'post_install')
class TestHrTimesheet(CommonTimesheetApproval):

    def test_01_check_auto_approve_timesheet(self):
    # Employees whose contracts are open and unmarked 'timesheet approve' (date_start < date < date_end)
        self.contract_employee_1.write({'timesheet_approval': False})
        timesheet = self.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'project_id': self.project.id,
            'employee_id': self.employee_1.id,
            'unit_amount': 1,
        })
        self.assertEqual(timesheet.timesheet_state, 'validate')

    def test_02_check_auto_approve_timesheet(self):
    # Employees whose contracts are open and marked 'timesheet approve' (date_start < date < date_end)
        timesheet = self.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'project_id': self.project.id,
            'employee_id': self.employee_1.id,
            'unit_amount': 1,
        })
        self.assertEqual(timesheet.timesheet_state, 'draft')

    def test_03_check_auto_approve_timesheet(self):
    # Employees whose contracts are open and unmarked 'timesheet approve' (date_start > date timesheet or date timesheet > date_end)
        self.contract_employee_1.write({'timesheet_approval': False})
        timesheet = self.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'project_id': self.project.id,
            'employee_id': self.employee_1.id,
            'unit_amount': 1,
            'date': date(2021, 9, 10)
        })
        self.assertEqual(timesheet.timesheet_state, 'draft')

    def test_04_check_auto_approve_timesheet(self):
    # Employee without contract
        timesheet = self.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 2',
            'project_id': self.project.id,
            'employee_id': self.employee_2.id,
            'unit_amount': 1,
        })
        self.assertEqual(timesheet.timesheet_state, 'draft')

    def test_05_check_auto_approve_timesheet(self):
    # User have no employees. create timesheet
        self.employee_2.write({'user_id': False})
        self.project.message_subscribe(partner_ids=self.user_no_employee.partner_id.ids)
        timesheet = self.env['account.analytic.line'].with_context(user_id=self.user_no_employee.id).create({
            'name': 'Timesheet Demo',
            'project_id': self.project.id,
            'unit_amount': 1,
        })
        self.assertEqual(timesheet.timesheet_state, 'validate')
