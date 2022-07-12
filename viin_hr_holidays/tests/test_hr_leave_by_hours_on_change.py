from unittest.mock import patch
from datetime import datetime, date
from odoo.tests import TransactionCase, Form, tagged
from odoo import fields
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestHrLeaveByHour(TransactionCase):

    def setUp(self):
        super(TestHrLeaveByHour, self).setUp()

        self.test_leave_type = self.env['hr.leave.type'].create({
            'name': 'Test Time-off Type',
            'leave_validation_type': 'hr',
            'allocation_type': 'no',
            'validity_start': False,
        })
        self.employee = self.env['hr.employee'].create({
            'name': 'Demo 1',
            'resource_calendar_id': self.env.ref('resource.resource_calendar_std').id
        })

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2021-09-12 09:01:02'))
    def test_01_on_change_by_hour(self):
        f = Form(self.env['hr.leave'])
        f.holiday_status_id = self.test_leave_type

        self.assertFalse(f.request_unit_hours, "Error testing: Time-off unit should be 'Day' by default. Here it is 'Hour'.")

        # Click on this selectbox option to trigger the onchange function
        f.request_unit_hours = True

        test_now_date = fields.Datetime.now().replace(second=0)

        self.assertEqual(f.date_from, test_now_date, "Error testing: FROM datetime and datetime now is not identical.")
        self.assertEqual(f.date_to, test_now_date, "Error testing: TO datetime and datetime now is not identical.")

    def test_adjust_dates_1(self):
        """
        Điều chỉnh ngày của xin nghỉ đã duyệt thành công
        """
        leave = self.env['hr.leave'].create({
            'name': 'Demo leaves',
            'employee_id': self.employee.id,
            'date_from': datetime(2021, 10, 5, 6, 0),
            'date_to': datetime(2021, 10, 8, 15, 0),
            'holiday_status_id': self.test_leave_type.id
            })
        # durations: 4 days - 32 hours
        leave.action_validate()

        # durations: 2 days - 12 hours
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': date(2021, 10, 5),
            'date_to': date(2021, 10, 6),
        })
        wizard.action_confirm()
        self.assertRecordValues(leave, [{
            'date_from': datetime(2021, 10, 5, 6, 0),
            'date_to': datetime(2021, 10, 6, 15, 0),
            'number_of_days': 2,
            'number_of_days_display': 2,
            'number_of_hours_display': 16,
            'duration_display': '2 days'
        }])
        rs_leaves = self.env['resource.calendar.leaves'].search([('holiday_id', '=', leave.id)])
        self.assertRecordValues(rs_leaves, [{
            'date_from': datetime(2021, 10, 5, 6, 0),
            'date_to': datetime(2021, 10, 6, 15, 0),
        }])

    def test_adjust_dates_2(self):
        """
        Điều chỉnh Ngày bắt đầu > ngày kết thúc
        => Không thành công
        """
        leave = self.env['hr.leave'].create({
            'name': 'Demo leaves',
            'employee_id': self.employee.id,
            'date_from': datetime(2021, 10, 5, 6, 0),
            'date_to': datetime(2021, 10, 8, 15, 0),
            'holiday_status_id': self.test_leave_type.id
            })
        leave.action_validate()

        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': date(2021, 10, 10),
            'date_to': date(2021, 10, 8),
        })
        self.assertRaises(UserError, wizard.action_confirm)

    def test_adjust_dates_3(self):
        """
        Kiểu nghỉ có chế độ tính toán là giờ
        => Không thành công
        """
        self.test_leave_type.write({
            'request_unit': 'hour'
        })
        leave = self.env['hr.leave'].create({
            'name': 'Demo leaves',
            'employee_id': self.employee.id,
            'date_from': datetime(2021, 10, 5, 6, 0),
            'date_to': datetime(2021, 10, 8, 15, 0),
            'holiday_status_id': self.test_leave_type.id
            })
        leave.action_validate()

        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': date(2021, 10, 5),
            'date_to': date(2021, 10, 10),
        })
        self.assertRaises(UserError, wizard.action_confirm)

    def test_adjust_dates_4(self):
        """
        Kiểu nghỉ có chế độ tính toán là nửa ngày
        => Không thành công
        """
        self.test_leave_type.write({
            'request_unit': 'half_day'
        })
        leave = self.env['hr.leave'].create({
            'name': 'Demo leaves',
            'employee_id': self.employee.id,
            'date_from': datetime(2021, 10, 5, 6, 0),
            'date_to': datetime(2021, 10, 8, 15, 0),
            'holiday_status_id': self.test_leave_type.id
            })
        leave.action_validate()

        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': date(2021, 10, 5),
            'date_to': date(2021, 10, 10),
        })
        self.assertRaises(UserError, wizard.action_confirm)

    def test_01_onchange_allocation_type(self):
        leave_type = Form(self.env['hr.leave.type'])
        leave_type.allocation_type = 'fixed_allocation'
        self.assertEqual(leave_type.allocation_validation_type, 'manager')
        leave_type.allocation_type = 'no'
        self.assertFalse(leave_type.allocation_validation_type)
        leave_type.allocation_type = 'fixed'
        self.assertFalse(leave_type.allocation_validation_type)

    def test_02_onchange_allocation_type(self):
        leave_type = self.env['hr.leave.type'].create({
            'name': 'Test Time-off Type 1',
            'leave_validation_type': 'hr',
            'allocation_type': 'fixed_allocation',
            'allocation_validation_type': 'both',
            'validity_start': False,
        })
        leave_type = Form(leave_type)
        leave_type.allocation_type = 'no'
        self.assertFalse(leave_type.allocation_validation_type)
        leave_type.allocation_type = 'fixed'
        self.assertFalse(leave_type.allocation_validation_type)
        leave_type.allocation_type = 'fixed_allocation'
        self.assertEqual(leave_type.allocation_validation_type, 'both')
