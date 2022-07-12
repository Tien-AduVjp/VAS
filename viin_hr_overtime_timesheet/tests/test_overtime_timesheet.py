from unittest.mock import patch
from datetime import datetime,date

from odoo.tests import tagged
from odoo import fields
from odoo.addons.viin_hr_overtime.tests.common import Common


@tagged('post_install', '-at_install')
class TestOvertimeTimeSheet(Common):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_01 = cls.env.ref('project.project_project_1')

    def _float_time_to_utc(self, date, float_time):
        return self.env['to.base'].convert_time_to_utc(datetime.combine(date, self.env['to.base'].float_hours_to_time(float_time)), self.env.user.tz, naive=True)

    def _calculate_matched_unmatched_hours_overtime_timesheet(self, plan_date, ot_lines, employee_id):
        """
            Phương thức này sẽ tính thời gian chấm công trùng và không trùng khớp giờ kế hoạch tăng ca.
        """
        related_hr_timesheet = self.env['account.analytic.line'].search([
                ('employee_id', '=', employee_id),
                ('project_id', '!=', False),
                ('date_start', '!=', False),
                ('date_end', '!=', False),
                ('date_start', '<', self._float_time_to_utc(plan_date, ot_lines[-1][1][1])),
                ('date_end', '>', self._float_time_to_utc(plan_date, ot_lines[0][1][0]))
            ])
        for k, line in enumerate(ot_lines):
            ot_lines[k] = list(line)
            matched_hours = unmatched_hours = 0.0
            _ , (time_start, time_end) = line
            ot_date_start = self._float_time_to_utc(plan_date, time_start)
            ot_date_end = self._float_time_to_utc(plan_date, time_end)
            for timesheet in related_hr_timesheet:
                if timesheet.date_start >= ot_date_end or timesheet.date_end <= ot_date_start:
                    continue
                period = [ot_date_start, ot_date_end]
                period.extend([timesheet.date_start, timesheet.date_end])
                period = sorted(period)
                if timesheet.date_start < ot_date_start:
                    unmatched_hours += (period[1] - period[0]).total_seconds() / 3600
                if timesheet.date_end > ot_date_end:
                    unmatched_hours += (period[3] - period[2]).total_seconds() / 3600
                matched_hours += (period[2] - period[1]).total_seconds() / 3600
            ot_lines[k].append((matched_hours, unmatched_hours))
        return ot_lines

    def test_01_matched_overtime_timesheet_hours(self):
        """
            Test Case 01: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công không nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian chấm công TRƯỚC khoảng thời gian tăng ca SỚM NHẤT của dòng kế hoạch tăng ca.
            Expect: Kế hoạch tăng ca không khớp chấm công, thông tin kế hoạch tăng ca không thay đổi.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':17.0,
                'unit_amount':2.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 0.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 0.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_02_matched_overtime_timesheet_hours(self):
        """
            Test Case 02: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm không trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian chấm công SAU khoảng thời gian tăng ca MUỘN NHẤT của dòng kế hoạch tăng ca.
            Expect: Kế hoạch tăng ca không khớp chấm công, thông tin kế hoạch tăng ca không thay đổi.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.date.today(),
                'time_start':21.0,
                'unit_amount':2.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 0.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 0.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_03_matched_overtime_timesheet_hours(self):
        """
            Test Case 03: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công không nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu và kết thúc chấm công trùng khớp với thời gian đăng ký tăng ca.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng bằng tổng thời gian chấm công.
                    Tổng số giờ không khớp chấm công bằng 0.0 giờ.
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.0,
                'unit_amount':2.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_04_matched_overtime_timesheet_hours(self):
        """
            Test Case 04: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công ĐÚNG giờ bắt đầu, thời gian kết thúc chấm công SỚM HƠN giờ kết thúc kế hoạch.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng tổng thời gian chấm công.
                    Tổng số giờ không khớp chấm công băng 0.0 giờ.
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.0,
                'unit_amount':1.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_05_matched_overtime_timesheet_hours(self):
        """
            Test Case 05: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công ĐÚNG giờ bắt đầu, thời gian kết thúc chấm công MUỘN HƠN giờ kết thúc kế hoạch.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng tổng thời gian kế hoạch.
                    Tổng số giờ không khớp chấm công bằng khoảng thời gian từ kết thúc kế hoạch tăng ca đến lúc chấm công ra.
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.0,
                'unit_amount':3.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 1.0)

    def test_06_matched_overtime_timesheet_hours(self):
        """
            Test Case 06: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công SỚM hơn giờ bắt đầu, thời gian kết thúc chấm công ĐÚNG giờ kết thúc kế hoạch tăng ca.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng tổng thời gian kế hoạch.
                    Tổng số giờ không khớp chấm công bằng khoảng thời gian từ lúc bắt đầu chấm công đến lúc bắt đầu kế hoạch tăng ca.
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':18.0,
                'unit_amount':3.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 1.0)

    def test_07_matched_overtime_timesheet_hours(self):
        """
            Test Case 07: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công SỚM giờ bắt đầu, thời gian kết thúc chấm công SỚM HƠN giờ kết thúc kế hoạch tăng ca.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng khoảng thời gian từ lúc bắt đầu kế hoạch tăng ca đế lúc kết thúc chấm công.
                    Tổng số giờ không khớp chấm công bằng khoảng thời gian từ lúc bắt đầu chấm công đến lúc bắt đầu kế hoạch tăng ca.
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':18.0,
                'unit_amount':2.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 1.0)

    def test_08_matched_overtime_timesheet_hours(self):
        """
            Test Case 08: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công SỚM hơn giờ bắt đầu, thời gian kết thúc chấm công MUỘN HƠN giờ kết thúc kế hoạch tăng ca.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng tổng thời gian trong kế hoạch tăng ca.
                    Tổng số giờ không khớp chấm công bằng khoảng thời gian từ lúc bắt đầu chấm công đến lúc bắt đầu kế hoạch tăng ca\
                    cộng với khoảng thời gian từ lúc kết thúc trong kế hoạch tăng ca đến lúc kết thúc chấm công
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':18.0,
                'unit_amount':4.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 2.0)

    def test_09_matched_overtime_timesheet_hours(self):
        """
            Test Case 09: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công MUỘN hơn giờ bắt đầu, thời gian kết thúc chấm công ĐÚNG giờ kết thúc kế hoạch tăng ca.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng khoảng thời gian từ lúc chấm công đên lúc kết thúc chấm công.
                    Tổng số giờ không khớp chấm công bằng 0.0 giờ
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':20.0,
                'unit_amount':1.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_10_matched_overtime_timesheet_hours(self):
        """
            Test Case 10: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công MUỘN hơn giờ bắt đầu, thời gian kết thúc chấm công SỚM hơn giờ kết thúc kế hoạch tăng ca.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng khoảng thời gian chấm công.
                    Tổng số giờ không khớp chấm công bằng 0.0 giờ.
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.5,
                'unit_amount':1.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_11_matched_overtime_timesheet_hours(self):
        """
            Test Case 11: Kiểm tra dữ liệu chấm công trùng khớp với thời gian đăng ký tăng ca khi dữ liệu chấm công nằm trong khoảng thời gian kế hoạch tăng ca.
            Input: Thời gian bắt đầu chấm công MUỘN hơn giờ băt đâu, thời gian kết thúc chấm công MUỘN hơn giờ kết thúc kế hoạch tăng ca.
            Expect: Tổng số giờ khớp chấm công trong dòng đăng ký tăng ca bằng khoảng thời gian từ lúc bắt đầu chấm công đến lúc kết thúc kế hoạch tăng ca.
                    Tổng số giờ không khớp chấm công bằng thời gian từ lúc kết thúc kế hoạch tăng ca đến lúc kết thúc chấm công.
                    Thời gian này nằm trong dòng tăng ca có khoảng thời gian tương ứng.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':20.0,
                'unit_amount':2.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 1.0)

    def test_12_matched_overtime_timesheet_hours(self):
        """
            Test case 12: Cập nhật thời gian trùng khớp/ không trùng khớp khi thay đổi thời gian chấm công.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':21.0,
                'time_start':19.0
            })
            timesheet = self.env['account.analytic.line'].create({
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':20.0,
                'unit_amount':2.0,
                'project_id':self.project_01.id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 1.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 1.0)
            timesheet.update({
                'time_start':18.0,
                'unit_amount':4.0
            })
            # rematch timesheet hours
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 2.0)

    def test_13_matched_overtime_timesheet_hours(self):
        """
            Test case 13: Kiểm tra tính toán thời gian trùng khớp/không trùng khớp thời gian chấm công và kế hoạch tăng ca.
            Input: chấm công trong nhiều task của dự án đã chọn.
            Expect: Giờ chấm công khớp: cộng tất cả thời gian trên các task đã chấm.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':18.0
            })
            self.env['account.analytic.line'].create(
                [
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':18.0,
                        'unit_amount':2.0,
                        'project_id':self.project_01.id,
                        'task_id':self.env.ref('project.project_task_1').id
                    },
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':20.0,
                        'unit_amount':2.0,
                        'project_id':self.project_01.id,
                        'task_id':self.env.ref('project.project_task_2').id
                    }
                ]
            )
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 4.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 4.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_14_matched_overtime_timesheet_hours(self):
        """
            Test case 14: Kiểm tra tính toán thời gian trùng khớp/không trùng khớp thời gian chấm công và kế hoạch tăng ca.
            Input: Chấm công nhiều lần trong cùng 1 task của cùng 1 dự án.
            Expect: Giờ chấm công khớp: cộng tất cả thời gian trên task đã chấm.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':22.0,
                'time_start':18.0
            })
            self.env['account.analytic.line'].create(
                [
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':18.0,
                        'unit_amount':4.0,
                        'project_id':self.project_01.id,
                        'task_id':self.env.ref('project.project_task_1').id
                    },
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':18.0,
                        'unit_amount':4.0,
                        'project_id':self.project_01.id,
                        'task_id':self.env.ref('project.project_task_1').id
                    }
                ]
            )
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 8.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 8.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_15_matched_overtime_timesheet_hours(self):
        """
            Test case 15: Kiểm tra tính toán thời gian trùng khớp/không trùng khớp thời gian chấm công và kế hoạch tăng ca.
            Input: Trong khoảng thời gian kế hoạch tăng ca, chấm công task không thuộc dự án đã chọn.
            Expect: Giờ chấm công khớp: không tính thời gian chấm công của task đó.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':20.0,
                'time_start':18.0
            })
            self.env['account.analytic.line'].create(
                [
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':18.0,
                        'unit_amount':2.0,
                        'project_id':self.project_01.id,
                        'task_id':self.env.ref('project.project_task_1').id
                    },
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':18.0,
                        'unit_amount':2.0,
                        'project_id':self.env.ref('project.project_project_2').id,
                        'task_id':self.env.ref('project.project_task_8').id
                    }
                ]
            )
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 4.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].matched_timesheet_hours, 4.0)
            self.assertEqual(self.overtime_plan_emp_01.line_ids[0].unmatched_timesheet_hours, 0.0)

    def test_16_matched_overtime_timesheet_hours(self):
        """
            Test case 13: Kiểm tra tính toán thời gian trùng khớp/không trùng khớp thời gian chấm công và kế hoạch tăng ca.
            Input: Tạo kế hoạch tăng ca trong nhiều khoảng thời gian khác nhau.
                   Chấm công trong nhiều khoảng thời gian khác nhau.
            Expect: Thời gian chấm công trùng khớp và không trùng khớp của các dòng tăng ca tương ứng được tạo ra thỏa mãn như các test case 1->11
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            employee_02 = self.employee_01.copy()
            contracts_emp_02 = self.contracts_emp_01.copy()
            contracts_emp_02.employee_id = employee_02
            contracts_emp_02.date_start = date(2021,3,2)
            contracts_emp_02.action_start_contract()
            self.overtime_plan_emp_01.update({
                'employee_id':employee_02.id,
                'date':fields.Date.today(),
                'time_end':4.0,
                'time_start':0.0
            })
            self.overtime_plan_02_emp_01, self.overtime_plan_03_emp_01, self.overtime_plan_04_emp_01 = self.env['hr.overtime.plan'].create(
                [
                    {
                        'employee_id':employee_02.id,
                        'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                        'date':fields.Date.today(),
                        'time_end':13.0,
                        'time_start':4.0
                    },
                    {
                        'employee_id':employee_02.id,
                        'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                        'date':fields.Date.today(),
                        'time_end':19.0,
                        'time_start':13.0
                    },
                    {
                        'employee_id':employee_02.id,
                        'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                        'date':fields.Date.today(),
                        'time_end':23.5,
                        'time_start':19.0
                    }
                ]
            )
            self.env['account.analytic.line'].create(
                [
                    {
                        'name':'Research new project 01',
                        'employee_id':employee_02.id,
                        'date':fields.Date.today(),
                        'time_start':0.0,
                        'unit_amount':8.0,
                        'project_id':self.project_01.id
                    },
                    {
                        'name':'Research new project 02',
                        'employee_id':employee_02.id,
                        'date':fields.Date.today(),
                        'time_start':8.0,
                        'unit_amount':8.0,
                        'project_id':self.project_01.id
                    },
                    {
                        'name':'Research new project 03',
                        'employee_id':employee_02.id,
                        'date':fields.Date.today(),
                        'time_start':16.0,
                        'unit_amount':8.0,
                        'project_id':self.project_01.id
                    }
                ]
            )
            overtime_rule = self.env['hr.overtime.rule'].search([
                ('weekday', '=', str(fields.Date.today().weekday())),
                ('company_id', '=', employee_02.company_id.id),
                ('holiday', '=', False)
                ])
            for ot_plan in [self.overtime_plan_emp_01, self.overtime_plan_02_emp_01, self.overtime_plan_03_emp_01, self.overtime_plan_04_emp_01]:
                ot_lines = self._calculate_overtime_line(ot_plan, overtime_rule, ot_plan.employee_id.contract_id)
                ot_lines_matched_timesheet = self._calculate_matched_unmatched_hours_overtime_timesheet(ot_plan.date, ot_lines, ot_plan.employee_id.id)
                for k, line in enumerate(ot_plan.line_ids):
                    self.assertEqual(line.matched_timesheet_hours, ot_lines_matched_timesheet[k][2][0])
                    self.assertEqual(line.unmatched_timesheet_hours, ot_lines_matched_timesheet[k][2][1])

    #-----------------------------------------------------Method test-----------------------------------------------------------------#
    def test_17_compute_timesheet_ids(self):
        """
            Test compute overtime_plan.timesheet ids, overtime_plan.project_task_ids, overtime_plan.project_ids
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            self.overtime_plan_emp_01.update({
                'date':fields.Date.today(),
                'time_end':20.0,
                'time_start':18.0
            })
            timesheet_01, timesheet_02 = self.env['account.analytic.line'].create(
                [
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':17.0,
                        'unit_amount':2.0,
                        'project_id':self.project_01.id,
                        'task_id':self.env.ref('project.project_task_1').id
                    },
                    {
                        'name':'Research new project',
                        'employee_id':self.employee_01.id,
                        'date':fields.Date.today(),
                        'time_start':19.0,
                        'unit_amount':2.0,
                        'project_id':self.env.ref('project.project_project_2').id,
                        'task_id':self.env.ref('project.project_task_8').id
                    }
                ]
            )
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertEqual(self.overtime_plan_emp_01.matched_timesheet_hours, 2.0)
            self.assertEqual(self.overtime_plan_emp_01.timesheet_ids, timesheet_01 | timesheet_02)
            self.assertEqual(self.overtime_plan_emp_01.project_task_ids, timesheet_01.task_id | timesheet_02.task_id)
            self.assertEqual(self.overtime_plan_emp_01.project_ids, timesheet_01.project_id | timesheet_02.project_id)
