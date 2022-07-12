from datetime import datetime, date, time

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools import relativedelta
from odoo.tests.common import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestHrPayrollTimesheetWFH(Common):
    
    def _local_to_utc(self, dt, tz_name):
        if isinstance(dt, datetime):
            return self.env['to.base'].convert_time_to_utc(
                dt,
                tz_name=tz_name,
                is_dst=None,
                naive=True
                )
        elif isinstance(dt, date):
            return self.env['to.base'].convert_time_to_utc(
                datetime.combine(dt, time.min),
                tz_name=tz_name,
                is_dst=None,
                naive=True
                )
        else:
            raise ValidationError("Invalid given dt in `local_to_utc(dt, tz)`. It should be either datetime or date object.")
    
    def test_11_pow_timesheet_validation(self):
        """
        Auto-generated timesheet during time-off validation will not be able to be proof of work
        """
        with self.assertRaises(UserError):
            self.wfh_time_off_1.timesheet_ids[0].write({'pow_for_timeoff_id': self.wfh_time_off_1.id})
        with self.assertRaises(UserError):
            self.wfh_time_off_2.timesheet_ids[0].write({'pow_for_timeoff_id': self.wfh_time_off_1.id})
        with self.assertRaises(UserError):
            self.paid_time_off_1.timesheet_ids[0].write({'pow_for_timeoff_id': self.wfh_time_off_1.id})
        with self.assertRaises(UserError):
            self.unpaid_time_off.timesheet_ids[0].write({'pow_for_timeoff_id': self.wfh_time_off_1.id})
    
    def test_12_pow_timesheet_validation(self):
        try:
            self.env['account.analytic.line'].create({
                'name': 'Proof of work entry 1',
                'project_id': self.env.ref('project.project_project_2').id,
                'employee_id': self.user.employee_id.id,
                'date': self.start_of_week + relativedelta(days=2),
                'unit_amount': 5,
                'pow_for_timeoff_id': self.wfh_time_off_1.id
                })
        except Exception as e:
            self.fail(
                "It was expected to have Proof of work timesheet recorded successfully but it was failed with the following error:\n%s."
                % str(e)
                )

    def test_13_pow_timesheet_validation(self):
        try:
            self.env['account.analytic.line'].create([
                {
                    'name': 'Proof of work entry 1',
                    'project_id': self.env.ref('project.project_project_2').id,
                    'employee_id': self.user.employee_id.id,
                    'date': self.start_of_week + relativedelta(days=2),
                    'unit_amount': 5,
                    'pow_for_timeoff_id': self.wfh_time_off_1.id
                    },
                {
                    'name': 'Proof of work entry 2',
                    'project_id': self.env.ref('project.project_project_2').id,
                    'employee_id': self.user.employee_id.id,
                    'date': self.start_of_week + relativedelta(days=2),
                    'unit_amount': 4,
                    'pow_for_timeoff_id': self.wfh_time_off_1.id
                    }
                ])
        except Exception as e:
            self.fail(
                "It was expected to have Proof of work timesheet recorded successfully but it was failed with the following error:\n%s."
                % str(e)
                )

        with self.assertRaises(UserError):
            self.env['account.analytic.line'].create({
                'name': 'Proof of work entry 2',
                'project_id': self.env.ref('project.project_project_2').id,
                'employee_id': self.user.employee_id.id,
                'date': self.start_of_week + relativedelta(days=2),
                'unit_amount': 4,
                'pow_for_timeoff_id': self.wfh_time_off_1.id
                })

    def test_14_pow_timesheet_validation(self):
        try:
            self.env['account.analytic.line'].create([
                {
                    'name': 'Proof of work entry 1',
                    'project_id': self.env.ref('project.project_project_2').id,
                    'employee_id': self.user.employee_id.id,
                    'date': self.start_of_week + relativedelta(days=3),
                    'unit_amount': 1,
                    'pow_for_timeoff_id': self.wfh_time_off_1.id
                    },
                {
                    'name': 'Proof of work entry 1',
                    'project_id': self.env.ref('project.project_project_2').id,
                    'employee_id': self.user.employee_id.id,
                    'date': self.start_of_week + relativedelta(days=3),
                    'unit_amount': 9,
                    'pow_for_timeoff_id': self.wfh_time_off_1.id
                    }
                ])
        except Exception as e:
            self.fail(
                "It was expected to have Proof of work timesheet recorded successfully but it was failed with the following error:\n%s."
                % str(e)
                )
        with self.assertRaises(UserError):
            self.env['account.analytic.line'].create({
                'name': 'Proof of work entry 1',
                'project_id': self.env.ref('project.project_project_2').id,
                'employee_id': self.user.employee_id.id,
                'date': self.start_of_week + relativedelta(days=3),
                'unit_amount': 1,
                'pow_for_timeoff_id': self.wfh_time_off_1.id
                })

    def test_21_pow_timesheet_recognition(self):
        timesheet = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 1',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=2),
            'unit_amount': 4,
            })
        self.assertTrue(timesheet.pow_for_timeoff_id, "The timesheet %s should be PoW.")
        timesheet = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 2',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=2),
            'unit_amount': 4,
            })
        self.assertTrue(timesheet.pow_for_timeoff_id, "The timesheet %s should be PoW.")
        timesheet = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 5,
            })
        self.assertTrue(timesheet.pow_for_timeoff_id, "The timesheet %s should be PoW.")

    def test_22_pow_timesheet_recognition(self):
        # Multiple timesheet records per day
        timesheet1 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-1',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 1,
            })
        timesheet2 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-2',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 3,
            })
        timesheet3 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-3',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 1,
            })
        timesheet4 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-4',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 1,
            })
        self.assertTrue(timesheet1.pow_for_timeoff_id, "The timesheet %s should be PoW.")
        self.assertTrue(timesheet2.pow_for_timeoff_id, "The timesheet %s should be PoW.")
        self.assertTrue(timesheet3.pow_for_timeoff_id, "The timesheet %s should be PoW.")
        self.assertFalse(timesheet4.pow_for_timeoff_id, "The timesheet %s should not be PoW.")

    def test_23_pow_timesheet_recognition(self):
        # Multiple timesheet records per day
        timesheet1 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-1',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 4,
            })
        timesheet2 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-3',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 2,
            })
        timesheet3 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-4',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 1,
            })
        self.assertTrue(timesheet1.pow_for_timeoff_id, "The timesheet %s should be PoW.")
        self.assertTrue(timesheet2.pow_for_timeoff_id, "The timesheet %s should be PoW.")
        self.assertFalse(timesheet3.pow_for_timeoff_id, "The timesheet %s should not be PoW.")
    
    def test_25_pow_timesheet_recognition(self):
        timesheet = self.env['account.analytic.line'].create({
            'name': 'Non-PoW Entry 1',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=1),
            'unit_amount': 4,
            })
        self.assertFalse(timesheet.pow_for_timeoff_id, "The timesheet %s should not be PoW.")

    def test_26_pow_timesheet_recognition(self):
        tz_name = self.user.employee_id.resource_calendar_id.tz
        partial_day_wfh_time_off = self.hr_leave_obj.create({
            'name': 'Work From home 1',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.wfh_time_off_type.id,
            'date_from': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=3), time(15, 0, 0)), tz_name),
            'date_to': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=3), time(17, 0, 0)), tz_name),
            'timesheet_project_id': self.env.ref('project.project_project_2').id,
            'timesheet_task_id': self.env.ref('project.project_task_12').id,
            'number_of_days': 1,
        })
        partial_day_wfh_time_off.action_validate()
        timesheet1 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-1',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 4,
            })
        timesheet2 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-3',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 2,
            })
        timesheet3 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-4',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 1,
            })
        timesheet4 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-4',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 2,
            })
        timesheet5 = self.env['account.analytic.line'].create({
            'name': 'PoW Entry 3-4',
            'project_id': self.env.ref('project.project_project_1').id,
            'employee_id': self.user.employee_id.id,
            'date': self.start_of_week + relativedelta(days=3),
            'unit_amount': 2,
            })
        self.assertTrue(timesheet1.pow_for_timeoff_id == self.wfh_time_off_1, "The timesheet %s should be PoW." % timesheet1.display_name)
        self.assertTrue(timesheet2.pow_for_timeoff_id == self.wfh_time_off_1, "The timesheet %s should be PoW." % timesheet2.display_name)
        self.assertTrue(timesheet3.pow_for_timeoff_id == partial_day_wfh_time_off, "The timesheet %s should be PoW." % timesheet3.display_name)
        self.assertTrue(timesheet4.pow_for_timeoff_id == partial_day_wfh_time_off, "The timesheet %s should be PoW." % timesheet4.display_name)
        self.assertFalse(timesheet5.pow_for_timeoff_id, "The timesheet %s should not be PoW." % timesheet5.display_name)

    def test_32_payslips(self):
        with self.env.cr.savepoint():
            non_pow_ts = self.env['account.analytic.line'].create({
                'name': 'Non Proof of work entry',
                'project_id': self.env.ref('project.project_project_1').id,
                'employee_id': self.user.employee_id.id,
                'date': self.start_of_week + relativedelta(days=1),
                'unit_amount': 4,
                })
            pow_ts = self.env['account.analytic.line'].create(
                [
                    {
                        'name': 'Proof of work entry 1',
                        'project_id': self.env.ref('project.project_project_1').id,
                        'employee_id': self.user.employee_id.id,
                        'date': self.start_of_week + relativedelta(days=2),
                        'unit_amount': 4,
                        },
                    {
                        'name': 'Proof of work entry 2',
                        'project_id': self.env.ref('project.project_project_1').id,
                        'employee_id': self.user.employee_id.id,
                        'date': self.start_of_week + relativedelta(days=3),
                        'unit_amount': 3,
                        }
                    ]
                )
            payslip = self.env['hr.payslip'].create({
                'employee_id': self.user.employee_id.id,
                'contract_id': self.user.employee_id.contract_ids[0].id,
                'company_id': self.env.company.id,
                'date_from': fields.Date.start_of(self.today, 'month'),
                'date_to': fields.Date.end_of(self.today, 'month'),
                'salary_cycle_id': self.env.company.salary_cycle_id.id,
            })
        self.assertNotIn(
            non_pow_ts.id,
            payslip.pow_timesheet_ids.ids,
            "The timesheet entry `%s` should not in the payslip PoW Timesheet Entries"
            )
        self.assertRecordValues(payslip, [
            {'pow_timesheet_ids': pow_ts.ids, 'pow_required_hours': 18.0, 'pow_timesheet_hours': 7.0, 'missing_pow_hours': 11.0}
            ])

    def test_33_payslips(self):
        last_month_today = self.today + relativedelta(months=-1)
        last_month_start_of_week = fields.Date.start_of(last_month_today, 'week')
        with self.env.cr.savepoint():
            wfh_time_off_last_month = self.hr_leave_obj.create({
                'name': 'Work From home 2',
                'department_id': self.user.employee_id.department_id.id,
                'employee_id': self.user.employee_id.id,
                'holiday_status_id': self.wfh_time_off_type.id,
                'date_from': self._local_to_utc(datetime.combine(last_month_start_of_week, time(8, 0, 0)), self.user.employee_id.resource_calendar_id.tz),
                'date_to': self._local_to_utc(datetime.combine(last_month_start_of_week, time(14, 0, 0)), self.user.employee_id.resource_calendar_id.tz),
                'timesheet_project_id': self.env.ref('project.project_project_2').id,
                'timesheet_task_id': self.env.ref('project.project_task_12').id,
                'number_of_days': 1,
                })
            wfh_time_off_last_month.action_validate()
            last_month_pow_ts = self.env['account.analytic.line'].create({
                'name': 'Non Proof of work entry',
                'project_id': self.env.ref('project.project_project_1').id,
                'employee_id': self.user.employee_id.id,
                'date': last_month_start_of_week,
                'unit_amount': 4,
                })
            pow_ts = self.env['account.analytic.line'].create(
                [
                    {
                        'name': 'Proof of work entry 1',
                        'project_id': self.env.ref('project.project_project_1').id,
                        'employee_id': self.user.employee_id.id,
                        'date': self.start_of_week + relativedelta(days=2),
                        'unit_amount': 4,
                        },
                    {
                        'name': 'Proof of work entry 2',
                        'project_id': self.env.ref('project.project_project_1').id,
                        'employee_id': self.user.employee_id.id,
                        'date': self.start_of_week + relativedelta(days=3),
                        'unit_amount': 3,
                        }
                    ]
                )
            payslip = self.env['hr.payslip'].create({
                'employee_id': self.user.employee_id.id,
                'contract_id': self.user.employee_id.contract_ids[0].id,
                'company_id': self.env.company.id,
                'date_from': fields.Date.start_of(self.today, 'month'),
                'date_to': fields.Date.end_of(self.today, 'month'),
                'salary_cycle_id': self.env.company.salary_cycle_id.id,
            })
        self.assertNotIn(
            last_month_pow_ts.id,
            payslip.pow_timesheet_ids.ids,
            "The timesheet entry `%s` should not in the payslip PoW Timesheet Entries"
            )
        self.assertRecordValues(payslip, [
            {'pow_timesheet_ids': pow_ts.ids, 'pow_required_hours': 18.0, 'pow_timesheet_hours': 7.0, 'missing_pow_hours': 11.0}
            ])

    def test_41_non_timesheet_analytic_lines(self):
        analytic_commercial_marketing = self.env.ref('analytic.analytic_commercial_marketing')
        try:
            analytic_lines = self.env['account.analytic.line'].create([
                {
                    'name': 'Analytic Line 1',
                    'account_id': analytic_commercial_marketing.id,
                    'date': self.start_of_week + relativedelta(days=3),
                    'unit_amount': 2,
                    'amount': 6,
                    },
                {
                    'name': 'Analytic Line 3',
                    'account_id': analytic_commercial_marketing.id,
                    'date': self.start_of_week + relativedelta(days=3),
                    'unit_amount': 3,
                    'amount': 6,
                    },
                {
                    'name': 'Analytic Line 3',
                    'account_id': analytic_commercial_marketing.id,
                    'date': self.start_of_week + relativedelta(days=3),
                    'unit_amount': 3,
                    'amount': 6,
                    },
                ])
            self.assertFalse(
                analytic_lines.pow_for_timeoff_id,
                "Normal anylitic lines should not have pow_for_timeoff_id set."
                )
        except Exception as e:
            self.fail("Test creating analytic lines failed.")
        
