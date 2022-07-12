from datetime import datetime
from odoo.tests import tagged
from odoo import fields
from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollPayslip(TestPayrollCommon):

    @classmethod
    def setUpClass(cls):
        super(TestPayrollPayslip, cls).setUpClass()

        cls.employee = cls.create_employee('Employee VN')
        cls.rs_calendar = cls.env.ref('resource.resource_calendar_std').copy()
        cls.rs_calendar.write({
            'tz': 'Asia/Ho_Chi_Minh'
        })
        cls.employee.write({
            'resource_calendar_id': cls.rs_calendar.id,
            'tz': 'Asia/Ho_Chi_Minh',
        })

        cls.contract = cls.create_contract(cls.employee.id, fields.Date.from_string('2021-1-1'))
        cls.contract.write({
            'resource_calendar_id': cls.rs_calendar.id,
        })

    def test_other_tz_1(self):
        payslip = self.create_payslip(
            self.employee.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract.id)

        self.assertRecordValues(payslip, [
            {
                'calendar_working_days': 22,
                'calendar_working_hours': 176,
                'duty_working_days': 22,
                'duty_working_hours': 176,
                'worked_days': 22,
                'worked_hours': 176,
                'leave_days': 0,
                'leave_hours': 0,
                'unpaid_leave_days': 0,
                'unpaid_leave_hours': 0
            }])

    def test_other_tz_2(self):
        leave_type = self.env['hr.leave.type'].search(
            [('company_id', '=', self.env.company.id),
            ('unpaid', '=', True)], limit=1)
        leave_1 = self.create_holiday(
            'Leave 1',
            self.employee.id,
            leave_type.id,
            # UTC + 7 => 8-17h
            datetime(2021, 7, 7, 1, 0),
            datetime(2021, 7, 7, 10, 0))
        leave_2 = self.create_holiday(
            'Leave 1',
            self.employee.id,
            leave_type.id,
            # UTC + 7 => 8-12h
            datetime(2021, 7, 8, 1, 0),
            datetime(2021, 7, 8, 5, 0))
        leave_1.action_validate()
        leave_2.action_validate()

        payslip = self.create_payslip(
            self.employee.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract.id)

        self.assertRecordValues(payslip, [
            {
                'calendar_working_days': 22,
                'calendar_working_hours': 176,
                'duty_working_days': 22,
                'duty_working_hours': 176,
                'worked_days': 20.5,
                'worked_hours': 164,
                'leave_days': 1.5,
                'leave_hours': 12,
                'unpaid_leave_days': 1.5,
                'unpaid_leave_hours': 12
            }])

    def test_other_tz_3(self):
        self.rs_calendar.write({
            'tz': 'Europe/Brussels'
        })
        self.employee.write({
            'tz': 'Europe/Brussels'
        })

        leave_type = self.env['hr.leave.type'].search(
            [('company_id', '=', self.env.company.id),
            ('unpaid', '=', True)], limit=1)
        leave_1 = self.create_holiday(
            'Leave 1',
            self.employee.id,
            leave_type.id,
            # UTC + 2 => 8-17h
            datetime(2021, 7, 7, 6, 0),
            datetime(2021, 7, 7, 15, 0))
        leave_2 = self.create_holiday(
            'Leave 1',
            self.employee.id,
            leave_type.id,
            # UTC + 2 => 8-12h
            datetime(2021, 7, 8, 6, 0),
            datetime(2021, 7, 8, 10, 0))
        leave_1.action_validate()
        leave_2.action_validate()

        payslip = self.create_payslip(
            self.employee.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract.id)

        self.assertRecordValues(payslip, [
            {
                'calendar_working_days': 22,
                'calendar_working_hours': 176,
                'duty_working_days': 22,
                'duty_working_hours': 176,
                'worked_days': 20.5,
                'worked_hours': 164,
                'leave_days': 1.5,
                'leave_hours': 12,
                'unpaid_leave_days': 1.5,
                'unpaid_leave_hours': 12
            }])

    def test_other_tz_4(self):
        self.rs_calendar.write({
            'tz': 'Europe/Brussels'
        })

        leave_type = self.env['hr.leave.type'].search(
            [('company_id', '=', self.env.company.id),
            ('unpaid', '=', True)], limit=1)
        leave_1 = self.create_holiday(
            'Leave 1',
            self.employee.id,
            leave_type.id,
            # UTC + 7 => 8-17h
            datetime(2021, 7, 7, 1, 0),
            datetime(2021, 7, 7, 10, 0))
        leave_2 = self.create_holiday(
            'Leave 1',
            self.employee.id,
            leave_type.id,
            # UTC + 7 => 8-12h
            datetime(2021, 7, 8, 1, 0),
            datetime(2021, 7, 8, 5, 0))
        leave_1.action_validate()
        leave_2.action_validate()

        payslip = self.create_payslip(
            self.employee.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract.id)

        self.assertRecordValues(payslip, [
            {
                'calendar_working_days': 22,
                'calendar_working_hours': 176,
                'duty_working_days': 22,
                'duty_working_hours': 176,
                'worked_days': 20.5,
                'worked_hours': 164,
                'leave_days': 1.5,
                'leave_hours': 12,
                'unpaid_leave_days': 1.5,
                'unpaid_leave_hours': 12
            }])
