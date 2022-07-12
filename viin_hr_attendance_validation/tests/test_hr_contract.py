from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class TestHrContract(Common):

    @classmethod
    def setUpClass(cls):
        super(TestHrContract, cls).setUpClass()
        # Nhân viên có hợp đồng , với lịch làm việc 44h/tuần (thêm giờ làm sáng thứ 7)
        # hợp đồng ở trạng thái dự thảo
        resource = cls.employee_1.resource_calendar_id.copy()
        cls.env['resource.calendar.attendance'].create({
            'name': 'T7',
            'dayofweek': '5',
            'day_period': 'morning',
            'hour_from': 8,
            'hour_to': 12,
            'calendar_id': resource.id
        })

        cls.contract = cls.env['hr.contract'].create({
            'name': 'Contract 1',
            'employee_id': cls.employee_1.id,
            'date_start': '2021-09-01',
            'wage': 5000,
            'resource_calendar_id': resource.id,
            'state': 'draft'
        })

    def test_09_hr_contract(self):

        """
        1. Tạo chấm công vào thứ 7 => chấm công không hợp lệ
        2. Xác nhận hợp đồng của nhân viên với lịch làm việc vào thứ 7 => Chấm công t7 hợp lệ
        3. Thay đổi lịch làm việc của nhân viên về 40h/tuần. Hủy hợp đồng =>  chấm công t7 không hợp lệ
        """
        #1
        attendance = self.create_attendance(self.employee_1.id, '2021-09-04 06:00:00', '2021-09-04 10:00:00')
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #2
        self.contract.action_start_contract()
        attendance._compute_early_leave_hours()
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #3
        self.employee_1.write({
            'resource_calendar_id': self.env.ref('resource.resource_calendar_std').id
        })
        self.contract.action_cancel()
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
