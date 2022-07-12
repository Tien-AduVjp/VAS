from datetime import datetime, time

from odoo import fields
from odoo.tools import relativedelta
from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    
    def setUp(self):
        super(Common, self).setUp()
        self.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'tracking_disable': True,
        }
        self.env = self.env(context=dict(self.no_mailthread_features_ctx, **self.env.context))
        self.wfh_time_off_type = self.env.ref('viin_hr_payroll_timesheet_wfh.time_off_type_wfh')
        self.user = self.env.ref('base.user_demo')
        # hardcoded today as 15 of the month to ensure later tests run within a single month
        self.today = fields.Date.today() - relativedelta(day=15)
        contract = self.user.employee_id.contract_ids[-1:]
        contract.write({
            'date_start': fields.Date.start_of(self.today, 'year') - relativedelta(years=1),
            'date_end': False,
            'state':'open'
            })
        if self.user.employee_id.resource_calendar_id != contract.resource_calendar_id:
            self.user.employee_id.resource_calendar_id = contract.resource_calendar_id
        tz_name = self.user.employee_id.resource_calendar_id.tz
        self.start_of_week = fields.Date.start_of(self.today, 'week')

        # apply do_not_match_timesheet_for_pow context to avoid timesheet demo data created
        # by other modules may cause side effect to the tests
        self.hr_leave_obj = self.env['hr.leave'].with_context(do_not_match_timesheet_for_pow=True)
        self.paid_time_off_1 = self.hr_leave_obj.create({
            'name': 'Paid Time Off 2',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_cl').id,
            'date_from': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=1), time(8, 0, 0)), tz_name),
            'date_to': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=1), time(17, 0, 0)), tz_name),
            'timesheet_project_id': self.env.ref('project.project_project_1').id,
            'timesheet_task_id': self.env.ref('project.project_task_6').id,
            'number_of_days': 1,
        })

        self.wfh_time_off_1 = self.hr_leave_obj.create({
            'name': 'Work From home 1',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.wfh_time_off_type.id,
            'date_from': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=2), time(8, 0, 0)), tz_name),
            'date_to': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=3), time(14, 0, 0)), tz_name),
            'timesheet_project_id': self.env.ref('project.project_project_2').id,
            'timesheet_task_id': self.env.ref('project.project_task_12').id,
            'number_of_days': 1,
        })

        self.wfh_time_off_2 = self.hr_leave_obj.create({
            'name': 'Work From home 2',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.wfh_time_off_type.id,
            'date_from': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=4), time(8, 0, 0)), tz_name),
            'date_to': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(days=4), time(14, 0, 0)), tz_name),
            'timesheet_project_id': self.env.ref('project.project_project_2').id,
            'timesheet_task_id': self.env.ref('project.project_task_12').id,
            'number_of_days': 1,
        })
        
        self.unpaid_time_off = self.hr_leave_obj.create({
            'name': 'Unpaid Time-off',
            'department_id': self.user.employee_id.department_id.id,
            'employee_id': self.user.employee_id.id,
            'holiday_status_id': self.env.ref('hr_holidays.holiday_status_unpaid').id,
            'date_from': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(weeks=1, days=1), time(8, 0, 0)), tz_name),
            'date_to': self._local_to_utc(datetime.combine(self.start_of_week + relativedelta(weeks=1, days=1), time(17, 0, 0)), tz_name),
            'timesheet_project_id': self.env.ref('project.project_project_1').id,
            'timesheet_task_id': self.env.ref('project.project_task_6').id,
            'number_of_days': 1,
        })

        (
            self.paid_time_off_1 + self.wfh_time_off_1 + self.wfh_time_off_2 + self.unpaid_time_off
            ).action_validate()
