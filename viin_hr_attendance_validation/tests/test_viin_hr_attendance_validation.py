from odoo.tests.common import tagged
from .common import Common


@tagged('post_install', '-at_install')
class TestViinHrAttendanceValidation(Common):

    def test_01_valid_worked_hours(self):
        # case 1: Test giờ chấm công hợp lệ = 0, không tính số giờ đi muộn về sớm
        # 1: Chỉ có checkin
        attendance_1 = self.create_attendance(self.employee_1.id, '2021-09-06 09:00:00')
        self.assertRecordValues(
            attendance_1,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        attendance_1.unlink()
        
        # 2: Checkin - checkout trước 8h sáng
        attendance_2 = self.create_attendance(self.employee_1.id, '2021-09-06 05:00:00', '2021-09-06 06:00:00')
        self.assertRecordValues(
            attendance_2,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        # 3: Checkin - checkout trong thời gian nghỉ trưa
        attendance_3 = self.create_attendance(self.employee_1.id, '2021-09-06 10:00:00', '2021-09-06 11:00:00')
        self.assertRecordValues(
            attendance_3,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        # 4: Checkin - checkout sau 17h chiều
        attendance_4 = self.create_attendance(self.employee_1.id, '2021-09-06 15:00:00', '2021-09-06 17:00:00')
        self.assertRecordValues(
            attendance_4,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        # 5: Checkin - checkout không nằm trong lịch làm việc (Chủ nhật)
        attendance_5 = self.create_attendance(self.employee_1.id, '2021-09-12 06:00:00', '2021-09-12 15:00:00')
        self.assertRecordValues(
            attendance_5,
            [{
                'valid_worked_hours': 0,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

    def test_02_valid_worked_hours(self):
        # case 2: Có giờ làm việc hợp lệ, không đi muộn, không về sớm
        # 2.1
        attendance = self.create_attendance(self.employee_1.id, '2021-09-13 05:55:00', '2021-09-13 15:12:00')
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 2.2
        attendance.write({
            'check_in': '2021-09-13 05:55:00',
            'check_out': '2021-09-13 10:12:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 2.3
        attendance.write({
            'check_in': '2021-09-13 10:55:00',
            'check_out': '2021-09-13 15:12:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 2.4
        attendance.write({
            'check_in': '2021-09-13 06:00:00',
            'check_out': '2021-09-13 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 2.5
        attendance.write({
            'check_in': '2021-09-13 06:00:00',
            'check_out': '2021-09-13 10:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 2.6
        attendance.write({
            'check_in': '2021-09-13 11:00:00',
            'check_out': '2021-09-13 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 4,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])

    def test_03_valid_worked_hours(self):
        # case 3: Có giờ làm việc hợp lệ, đi muộn, không về sớm
        # 3.1
        attendance = self.create_attendance(self.employee_1.id, '2021-09-13 06:00:01', '2021-09-13 15:12:00')
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 7.999722222222222,
                'late_attendance_hours': 0.0002777777777777778,
                'early_leave_hours': 0
            }])
        
        # 3.2
        attendance.write({
            'check_in': '2021-09-13 06:00:01',
            'check_out': '2021-09-13 10:12:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 3.999722222222222,
                'late_attendance_hours': 0.0002777777777777778,
                'early_leave_hours': 0
            }])
        
        # 3.3
        attendance.write({
            'check_in': '2021-09-13 11:00:01',
            'check_out': '2021-09-13 15:12:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 3.999722222222222,
                'late_attendance_hours': 0.0002777777777777778,
                'early_leave_hours': 0
            }])
    
    def test_04_valid_worked_hours(self):
        # case 4: Có giờ làm việc hợp lệ, không đi muộn, về sớm
        # 4.1
        attendance = self.create_attendance(self.employee_1.id, '2021-09-13 06:00:00', '2021-09-13 14:59:59')
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 7.999722222222222,
                'late_attendance_hours': 0,
                'early_leave_hours': 0.0002777777777777778
            }])
        
        # 4.2
        attendance.write({
            'check_in': '2021-09-13 06:00:00',
            'check_out': '2021-09-13 09:59:59'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 3.999722222222222,
                'late_attendance_hours': 0,
                'early_leave_hours': 0.0002777777777777778
            }])
        
        # 4.3
        attendance.write({
            'check_in': '2021-09-13 11:00:00',
            'check_out': '2021-09-13 14:59:59'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 3.999722222222222,
                'late_attendance_hours': 0,
                'early_leave_hours': 0.0002777777777777778
            }])

    def test_05_valid_worked_hours(self):
        # case 5: Có giờ làm việc hợp lệ, đi muộn, về sớm
        # 5.1
        attendance = self.create_attendance(self.employee_1.id, '2021-09-13 06:00:01', '2021-09-13 14:59:59')
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 7.999444444444444,
                'late_attendance_hours': 0.0002777777777777778,
                'early_leave_hours': 0.0002777777777777778
            }])
        
        # 5.2
        attendance.write({
            'check_in': '2021-09-13 06:00:01',
            'check_out': '2021-09-13 09:59:59'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 3.9994444444444444,
                'late_attendance_hours': 0.0002777777777777778,
                'early_leave_hours': 0.0002777777777777778
            }])
        
        # 5.3
        attendance.write({
            'check_in': '2021-09-13 11:00:01',
            'check_out': '2021-09-13 14:59:59'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 3.9994444444444444,
                'late_attendance_hours': 0.0002777777777777778,
                'early_leave_hours': 0.0002777777777777778
            }])

    def test_06_valid_worked_hours(self):
        # case 6: Chấm công trong 2 ngày, có giờ hợp lệ
        # 6.1: Chấm công vào T6+T7, không đi muộn, không về sớm
        attendance = self.create_attendance(self.employee_1.id, '2021-09-03 05:50:00', '2021-09-04 14:00:00')
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 6.2: Chấm công vào CN+T2, không đi muộn, không về sớm
        attendance.write({
            'check_in': '2021-09-05 07:00:00',
            'check_out': '2021-09-06 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 6.3: Chấm công vào T3+T4, không đi muộn, không về sớm
        attendance.write({
            'check_in': '2021-09-07 05:50:00',
            'check_out': '2021-09-08 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 16,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 6.4: Chấm công vào T3+T4, không đi muộn, không về sớm
        attendance.write({
            'check_in': '2021-09-07 05:50:00',
            'check_out': '2021-09-08 10:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 12,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 6.5: Chấm công vào T3+T4, không đi muộn, không về sớm
        attendance.write({
            'check_in': '2021-09-07 11:00:00',
            'check_out': '2021-09-08 15:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 12,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 6.6: Chấm công vào T3+T4, không đi muộn, không về sớm
        attendance.write({
            'check_in': '2021-09-07 11:00:00',
            'check_out': '2021-09-08 10:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 8,
                'late_attendance_hours': 0,
                'early_leave_hours': 0
            }])
        
        # 6.7: Chấm công vào T3+T4, đi muộn, về sớm
        attendance.write({
            'check_in': '2021-09-07 07:00:00',
            'check_out': '2021-09-08 14:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 14,
                'late_attendance_hours': 1,
                'early_leave_hours': 1
            }])
        
        # 6.8: Chấm công vào T3+T4, đi muộn, về sớm
        attendance.write({
            'check_in': '2021-09-07 07:00:00',
            'check_out': '2021-09-08 09:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 10,
                'late_attendance_hours': 1,
                'early_leave_hours': 1
            }])
        
        # 6.9: Chấm công vào T3+T4, đi muộn, về sớm
        attendance.write({
            'check_in': '2021-09-07 12:00:00',
            'check_out': '2021-09-08 09:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 6,
                'late_attendance_hours': 1,
                'early_leave_hours': 1
            }])
        
        # 6.10: Chấm công vào T3+T4, đi muộn, về sớm
        attendance.write({
            'check_in': '2021-09-07 12:00:00',
            'check_out': '2021-09-08 14:00:00'
        })
        self.assertRecordValues(
            attendance,
            [{
                'valid_worked_hours': 10,
                'late_attendance_hours': 1,
                'early_leave_hours': 1
            }])
