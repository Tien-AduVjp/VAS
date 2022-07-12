from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class TestGlobalLeave(Common):

    @classmethod
    def setUpClass(cls):
        super(TestGlobalLeave, cls).setUpClass()
        # Nghỉ toàn cục vào cả ngày thứ 2, sáng thứ 3, chiều thứ 4
        cls.env.ref('resource.resource_calendar_std').write({
            'global_leave_ids': [(0, 0, {'date_from': '2021-09-06 06:00:00', 'date_to': '2021-09-06 15:00:00'}),
                                 (0, 0, {'date_from': '2021-09-07 06:00:00', 'date_to': '2021-09-07 10:00:00'}),
                                 (0, 0, {'date_from': '2021-09-08 11:00:00', 'date_to': '2021-09-08 15:00:00'})]
        })

    def test_07_global_leave(self):
        # Chấm công vào các ngyaf nghỉ toàn cục
        #7.1 Chấm công vào ngày nghỉ toàn cục t2 (cả ngày)
        attendance = self.create_attendance(self.employee_1.id, '2021-09-06 06:00:00', '2021-09-06 15:00:00')
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #7.2 Chấm công vào ngày nghỉ toàn cục t3 (buổi sáng)
        attendance.write({
            'check_in': '2021-09-07 06:00:00',
            'check_out': '2021-09-07 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #7.3 Chấm công vào ngày nghỉ toàn cục t3 (buổi sáng)
        attendance.write({
            'check_in': '2021-09-07 09:00:00',
            'check_out': '2021-09-07 17:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #7.4 Chấm công vào ngày nghỉ toàn cục t3 (buổi sáng)
        attendance.write({
            'check_in': '2021-09-07 12:00:00',
            'check_out': '2021-09-07 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 3,
                'late_attendance_hours': 1,
                'early_leave_hours': 0
            }])

        #7.5 Chấm công vào ngày nghỉ toàn cục t4 (buổi chiều)
        attendance.write({
            'check_in': '2021-09-08 06:00:00',
            'check_out': '2021-09-08 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #7.6 Chấm công vào ngày nghỉ toàn cục t4 (buổi chiều)
        attendance.write({
            'check_in': '2021-09-08 06:00:00',
            'check_out': '2021-09-08 13:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

    def test_08_global_leave(self):
        """
        1. Chấm công vào ngày t2, sau đó thiết lập ngày t2 đó là ngày nghỉ toàn cục
            => Thứ 2 chấm công không hợp lệ
        2. Tạo chấm công vào thứ 3, sau đó sửa ngày nghỉ toàn cục từ t2 sang t3
            => chấm công thứ 2 hợp lệ, chấm công thứ 3 không hợp lệ
        3. Xóa ngày nghỉ toàn cục vào thứ 3
            => chấm công thứ 2 và thứ 3 hợp lệ
        """
        resource = self.env.ref('resource.resource_calendar_std')
        resource.global_leave_ids.unlink()

        #1
        attendance_1 = self.create_attendance(self.employee_1.id, '2021-09-13 06:00:00', '2021-09-13 15:00:00')
        self.assertRecordValues(
            attendance_1,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        resource.write({
            'global_leave_ids': [(0, 0, {'date_from': '2021-09-13 06:00:00', 'date_to': '2021-09-13 15:00:00'})]
        })
        self.assertRecordValues(
            attendance_1,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #2
        attendance_2 = self.create_attendance(self.employee_1.id, '2021-09-14 06:00:00', '2021-09-14 15:00:00')
        self.assertRecordValues(
            attendance_2,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        resource.global_leave_ids[0].write({
            'date_from': '2021-09-14 06:00:00',
            'date_to': '2021-09-14 15:00:00'
        })
        self.assertRecordValues(
            attendance_1 | attendance_2,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            },
            {
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

        #3
        resource.global_leave_ids.unlink()
        self.assertRecordValues(
            attendance_1 | attendance_2,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            },
            {
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
