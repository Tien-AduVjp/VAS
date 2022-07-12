from datetime import date, datetime, time
from unittest.mock import patch

from odoo.tests import tagged
from odoo import fields

from odoo.addons.viin_hr_overtime.tests.common import Common
from odoo.addons.test_convert.tests.test_env import field


@tagged('post_install', '-at_install')
class TestOvertimeAttendance(Common):

    @classmethod
    def setUpClass(cls):
        super(TestOvertimeAttendance, cls).setUpClass()
        cls.float_hours_to_time = cls.env['to.base'].float_hours_to_time
        cls.env.company.overtime_recognition_mode = 'attendance'

    def float_time_to_utc(self, date, float_time):
        return self.env['to.base'].convert_time_to_utc(datetime.combine(date, self.float_hours_to_time(float_time)), self.env.user.tz, naive=True)

    def _calculate_matched_unmatched_attendance_hours(self, plan_date, employee_id, ot_lines):
        related_hr_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', employee_id),
                ('check_in', '<', self.float_time_to_utc(plan_date, ot_lines[-1][1][1])),
                ('check_out', '>', self.float_time_to_utc(plan_date, ot_lines[0][1][0]))
            ])
        for k, line in enumerate(ot_lines):
            ot_lines[k] = list(line)
            matched_hours = unmatched_hours = 0.0
            _ , (time_start, time_end) = line
            time_start = self.float_time_to_utc(plan_date, time_start)
            time_end = self.float_time_to_utc(plan_date, time_end)
            for attendance in related_hr_attendance:
                if attendance.check_in >= time_end or attendance.check_out <= time_start:
                    continue
                period = [time_start, time_end]
                period.extend([attendance.check_in, attendance.check_out])
                period = sorted(period)
                if attendance.check_in < time_start:
                    unmatched_hours += (period[1] - period[0]).total_seconds() / 3600
                if attendance.check_out > time_end:
                    unmatched_hours += (period[3] - period[2]).total_seconds() / 3600
                matched_hours += (period[2] - period[1]).total_seconds() / 3600
            ot_lines[k].append((matched_hours, unmatched_hours))
        return ot_lines

    def test_01_matched_overtime_attendance_hours(self):
        """
            Case 1: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt, thời gian đăng ký vào ra nằm NGOÀI khoảng thời gian tăng ca.
            Input: Thời gian đăng ký vào /ra TRƯỚC khoảng thời gian tăng ca sớm nhất của dòng kế hoạch tăng ca.
            Expect:
                +) Các trường tổng số giờ có mặt hợp lệ và không hợp lệ của các dòng kế hoạch tăng ca có giá trị bằng 0.0 giờ
                +) Tổng số giờ vào ra được khớp của kế hoặc tăng ca bằng 0.0 giờ.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':23.0,
                'time_start':20.0
               })

            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today() , time(8, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(17, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 0.0)
            for line in self.overtime_plan_emp_01.line_ids:
                self.assertEqual(line.matched_attendance_hours, 0.0)
                self.assertEqual(line.unmatched_attendance_hours, 0.0)

    def test_02_matched_overtime_attendance_hours(self):
        """
            Case 2: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm NGOÀI khoảng thời gian tăng ca.
            Input: Thời gian đăng ký vào/ra SAU khoảng thời gian tăng ca sớm nhất của dòng kế hoạch tăng ca.
            Expect:
                +) Các trường tổng số giờ có mặt hợp lệ và không hợp lệ của các dòng kế hoạch tăng ca có giá trị bằng 0.0 giờ
                +) Tổng số giờ vào ra được khớp của kế hoặc tăng ca bằng 0.0 giờ.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':4.0,
                'time_start':3.0
               })

            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(8, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(17, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 0.0)
            for line in self.overtime_plan_emp_01.line_ids:
                self.assertEqual(line.matched_attendance_hours, 0.0)
                self.assertEqual(line.unmatched_attendance_hours, 0.0)

    def test_03_matched_overtime_attendance_hours(self):
        """
            Case 3: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Thời gian đăng ký vào/ra NẰM TRONG khoảng thời gian kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian giữa 2 lần đăng ký vào / ra
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(18, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(20, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.0)

    def test_04_matched_overtime_attendance_hours(self):
        """
            Case 4: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký vào ĐÚNG GIỜ / đăng ký ra SỚM HƠN kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian giữa thời 2 lần đăng ký vào ra.
                    Thời gian có mặt không hợp lệ trên các dòng kế hoạch tăng ca bằng 0.0.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
        # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today() , time(18, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(19, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.0)

    def test_05_matched_overtime_attendance_hours(self):
        """
            Case 5: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký vào đúng giờ / đăng ký ra muộn hơn kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian giữa thời 2 lần đăng ký vào ra.
                    Thời gian có mặt không hợp là khoảng thời gian từ lúc kết thúc kế hoạch tăng ca để lúc đăng ký ra,
                    thời gian này nằm trên dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today() , time(18, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(21, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 1.0)

    def test_06_matched_overtime_attendance_hours(self):
        """
            Case 6: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký vào sớm / đăng ký ra đúng giờ so với kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian giữa thời 2 lần đăng ký vào ra.
                    Thời gian có mặt không hợp là khoảng thời gian từ lúc đăng kí vào và thời gian bắt đầu tăng ca,
                    thời gian này nằm trên dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(20, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 1.0)

    def test_07_matched_overtime_attendance_hours(self):
        """
            Case 7: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký vào sớm / đăng ký ra sớm so với kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian giữa thời gian bắt đầu kết hoạch tăng ca và thời gian đăng ký ra.
                    Thời gian có mặt không hợp là khoảng thời gian từ lúc đăng kí vào và thời gian bắt đầu tăng ca,
                    thời gian này nằm trên dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(19, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 1.0)

    def test_08_matched_overtime_attendance_hours(self):
        """
            Case 8: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký vào sớm / đăng ký ra muộn so với kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian giữa thời gian bắt đầu và kết thúc kế hoạch.
                    Thời gian có mặt không hợp lệ là khoảng thời gian từ lúc đăng kí vào và thời gian bắt đầu tăng ca cộng với khoảng thời gian kết thúc kế hoạch tăng ca đến lúc đăng ký ra
                    khoảng thời gian này nằm trên dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(21, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 2.0)

    def test_09_matched_overtime_attendance_hours(self):
        """
            Case 9: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký vào muộn / đăng ký ra đúng giờ so với kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian từ lúc đăng ký vào đến lúc kết thúc kế hoạch tăng ca.
                    Thời gian có mặt không hợp lệ bằng 0.0.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(19, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(20, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.0)

    def test_10_matched_overtime_attendance_hours(self):
        """
            Case 10: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký vào muộn / đăng ký ra sớm so với kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian từ lúc đăng ký vào đến lúc đăng ký ra.
                    Thời gian có mặt không hợp lệ bằng 0.0.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(18, 30)),
                'check_out':datetime.combine(fields.Date.today(), time(19, 30))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.0)

    def test_11_matched_overtime_attendance_hours(self):
        """
            Case 11: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. Thời gian đăng ký vào / ra nằm TRONG khoảng thời gian tăng ca.
            Input: Đăng ký VÀO MUỘN / đăng ký RA MUỘN so với kế hoạch tăng ca.
            Expect: Tông số giờ khớp có mặt trong kế hoạch tăng ca bằng khoảng thời gian từ lúc đăng ký vào đến lúc kết thúc kế hoạch tăng ca.
                    Thời gian có mặt không hợp lệ bằng khoảng thời gian từ lúc kết thúc kế hoạch tăng ca đến lúc đăng ký ra.
                    khoảng thời gian này nằm trên dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(18, 30)),
                'check_out':datetime.combine(fields.Date.today(), time(20, 30))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 1.5)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 1.5)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.5)

    def test_12_matched_overtime_attendance_hours(self):
        """
            Tăng ca: Chỉ đăng ký vào, không đăng ký ra.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(18, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 0.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 0.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.0)

    def test_13_matched_overtime_attendance_hours(self):
        """
            Chỉnh sửa giờ chấm công vào ra, tự động cập nhật dữ liệu. không cần nhấn khớp lệnh tăng ca mới tự động tính toán lại.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':20.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            attendance = self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_out':datetime.combine(fields.Date.today(), time(20, 0)),
                'check_in':datetime.combine(fields.Date.today(), time(18, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_attendance_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.0)
            attendance.update({
                'check_out':datetime.combine(fields.Date.today(), time(21, 0)),
                'check_in':datetime.combine(fields.Date.today(), time(17, 0))
            })
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 2.0)

    def test_14_matched_overtime_attendance_hours(self):
        """
            Case 14: Kiểm tra tính toán khớp vào ra với nhiều lần đăng ký vào ra.
            Input:
                - Tạo nhiều kế hoạch tăng ca ở các khoảng thời gian khác nhau.
                - Đăng ký vào/ra ở nhiều khoảng thời gian khác nhau.
            Expect: Các dòng tăng ca được tạo ra có các có khoảng thời gian có mặt hợp lệ và không hợp lệ tính toán thỏa mãn như test case 1 -> 11
            ...
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':23.9,
                'time_start':20.5
            })
            self.overtime_plan_02_emp_01, self.overtime_plan_03_emp_01 = self.env['hr.overtime.plan'].create([
                    {
                        'employee_id':self.employee_01.id,
                        'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                        'recognition_mode':'none',
                        'date':fields.Date.today(),
                        'time_end':6.0,
                        'time_start':1.0
                    },
                    {
                        'employee_id':self.employee_01.id,
                        'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                        'recognition_mode':'none',
                        'date':fields.Date.today(),
                        'time_end':20.0,
                        'time_start':6.5
                    }
                ]
            )
            self.env['hr.attendance'].create(
                [
                    {
                        'employee_id':self.employee_01.id,
                        'check_in':datetime.combine(fields.Date.today(), time(1, 0)),
                        'check_out':datetime.combine(fields.Date.today(), time(3, 20))
                    },
                    {
                        'employee_id':self.employee_01.id,
                        'check_in':datetime.combine(fields.Date.today(), time(4, 0)),
                        'check_out':datetime.combine(fields.Date.today(), time(7, 35))
                    },
                    {
                        'employee_id':self.employee_01.id,
                        'check_in':datetime.combine(fields.Date.today(), time(7, 43)),
                        'check_out':datetime.combine(fields.Date.today(), time(16, 34))
                    },
                    {
                        'employee_id':self.employee_01.id,
                        'check_in':datetime.combine(fields.Date.today(), time(16, 50)),
                        'check_out':datetime.combine(fields.Date.today(), time(23, 59))
                    }
                ])
            self.overtime_plan_emp_01.action_match_attendances()
            self.overtime_plan_02_emp_01.action_match_attendances()
            self.overtime_plan_03_emp_01.action_match_attendances()
            overtime_rule = self.env['hr.overtime.rule'].search([
                ('weekday', '=', str(self.overtime_plan_emp_01.date.weekday())),
                ('company_id', '=', self.overtime_plan_emp_01.employee_id.company_id.id),
                ('holiday', '=', False)
                ])
            for ot_plan in [self.overtime_plan_emp_01, self.overtime_plan_02_emp_01, self.overtime_plan_03_emp_01]:
                ot_lines = self._calculate_overtime_line(ot_plan, overtime_rule, ot_plan.employee_id.contract_id)
                ot_lines_matched_attendance = self._calculate_matched_unmatched_attendance_hours(ot_plan.date, ot_plan.employee_id.id, ot_lines)
                for k, line in enumerate(ot_plan.line_ids):
                    self.assertEqual(line.matched_attendance_hours, ot_lines_matched_attendance[k][2][0])
                    self.assertEqual(line.unmatched_attendance_hours, ot_lines_matched_attendance[k][2][1])

    def test_15_matched_overtime_attendance_hours(self):
        """
            Case 15: Kiểm tra dữ liệu vào/ra khớp với chế độ nhận diện tăng ca là có mặt. 
            Thời gan tăng ca nằm TRONG khoảng thời gian đăng ký vào ra.
            Input: Thời gan tăng ca nằm TRONG khoảng thời gian đăng ký vào ra.
            Expect: Thời gian tăng ca thực tế chính xác.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            # Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':19.0,
                'time_start':17.0
               })
            # Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(16, 0)),
                'check_out':datetime.combine(fields.Date.today(), time(20, 0))
            })
            self.overtime_plan_emp_01.action_match_attendances()
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].actual_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[1].actual_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_attendance_hours, 0.0)
