from datetime import datetime
from odoo.tests import SavepointCase, tagged
from odoo import fields
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestLeaveDetailsReport(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestLeaveDetailsReport, cls).setUpClass()
        cls.env['hr.leave.type'].search([('company_id', '=', cls.env.company.id)]).write({
            'validity_start': fields.Date.to_date('2021-01-01')
        })

        cls.unpaid_type = cls.env['hr.leave.type'].search(
            [('unpaid','=',True),
             ('company_id', '=', cls.env.company.id)],
            limit=1)

        cls.paid_type = cls.env['hr.leave.type'].search(
            [('unpaid','=',False),
             ('company_id', '=', cls.env.company.id)],
            limit=1)
        cls.paid_type.write({
            'allocation_type': 'no',
            'leave_validation_type': 'no_validation',
        })

        calendar = cls.env.ref('resource.resource_calendar_std').copy()
        calendar.tz = 'UTC'
        cls.employee_A = cls.env['hr.employee'].create({
            'name': 'Employee A',
            'resource_calendar_id': calendar.id,
            'tz': 'UTC'
        })
        cls.employee_B = cls.env['hr.employee'].create({
            'name': 'Employee B',
            'resource_calendar_id': calendar.id,
            'tz': 'UTC'
        })

    def create_leave(self, emoloyee, type, date_from, date_to):
        return self.env['hr.leave'].with_context(tracking_disable=True).create({
            'holiday_status_id': type.id,
            'employee_id': emoloyee.id,
            'holiday_type': 'employee',
            'date_from': date_from,
            'date_to': date_to
        })

    def test_report_1(self):
        """
        Nhân viên A:
            nghỉ không lương 3 ngày (24h) từ 1/11 đến 3/11
        Nhân viên B:
            - Nghỉ có lương 0.5 ngày (4h): sáng ngày 1/1
            - Nghỉ có lương 1h chiêu ngày 1/1, từ 16h đến 17h
        Output:
            Báo cáo nghỉ:
                Ngày 1/11:
                    Nhân viên A : 8h
                    Nhân viên B : 6h
                Ngày 2/11:
                    Nhân viên A : 8h
                Ngày 3/11:
                    Nhân viên A : 8h
        """
        self.create_leave(
            self.employee_A,
            self.unpaid_type,
            datetime(2021,11,1,8,0),
            datetime(2021,11,3,17,0))

        self.create_leave(
            self.employee_B,
            self.paid_type,
            datetime(2021,11,1,8,0),
            datetime(2021,11,1,12,0))

        self.create_leave(
            self.employee_B,
            self.paid_type,
            datetime(2021,11,1,16,0),
            datetime(2021,11,1,17,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-11-1 - Employee A
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-1 - employee B
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_B.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 5)
        self.assertEqual(data['duration_days'], 0.625)

        # 2021-11-2 - Employee A
        domain = [
            ('date', '=', '2021-11-2'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-3 - Employee A
        domain = [
            ('date', '=', '2021-11-3'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

    def test_report_2(self):
        """
        Nhân viên A:
            nghỉ không lương 5 ngày (32h) từ 1/11 đến 4/11
                Từ 13h ngày 1/11 đến 12h ngày 4/11 (24h trong 5 ngày)
        Nhân viên B:
            nghỉ có lương 2 ngày (16h) từ 1/11 đến 2/11

        Output:
            Báo cáo nghỉ:
                Ngày 1/1:
                    Nhân viên A : 4h
                    Nhân viên B : 8h
                Ngày 2/1:
                    Nhân viên A : 8h
                    Nhân viên B : 8h
                Ngày 3/1:
                    Nhân viên A : 8h
                Ngày 4/1:
                    Nhân viên A : 4h
        """
        self.create_leave(
            self.employee_A,
            self.unpaid_type,
            datetime(2021,11,1,13,0),
            datetime(2021,11,4,12,0))

        self.create_leave(
            self.employee_B,
            self.paid_type,
            datetime(2021,11,1,8,0),
            datetime(2021,11,2,17,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-11-1 - Employee A
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 4)
        self.assertEqual(data['duration_days'], 0.5)

        # 2021-11-1 - Employee B
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_B.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-2 - Employee A
        domain = [
            ('date', '=', '2021-11-2'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-2 - Employee B
        domain = [
            ('date', '=', '2021-11-2'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-3 - Employee A
        domain = [
            ('date', '=', '2021-11-3'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-4 - Employee A
        domain = [
            ('date', '=', '2021-11-4'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 4)
        self.assertEqual(data['duration_days'], 0.5)

    def test_report_3(self):
        """
        Nhân viên A:
            nghỉ không lương 4 ngày từ 5/11 đến 8/11

        Output:
            Báo cáo nghỉ:
                Ngày 5/11:
                    Nhân viên A : 8h
                Ngày 6/11 và 7/11 , không có thời gian nghỉ do là ngày thứ 7 và chủ nhật, không có trong lich làm việc
                Ngày 8/11:
                    Nhân viên A : 8h
        """
        self.create_leave(
            self.employee_A,
            self.unpaid_type,
            datetime(2021,11,5,8,0),
            datetime(2021,11,8,17,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-11-5 - Employee A
        domain = [
            ('date', '=', '2021-11-5'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-6,7  - Employee A
        domain = [
            ('date', '>=', '2021-11-6'),
            ('date', '<=', '2021-11-7'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)
        self.assertFalse(data)

        # 2021-11-8 - Employee A
        domain = [
            ('date', '=', '2021-11-8'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

    def test_report_4(self):
        """
        Nhân viên A:
            nghỉ không lương 4 ngày từ 28/10 đến 2/11

        Output:
            Báo cáo nghỉ: tổng thời gian nghỉ là 6 ngày (48h)
                Tháng 10: có 2 ngày nghỉ
                    Ngày 28/10:
                        Nhân viên A : 8h
                    Ngày 29/10:
                        Nhân viên A : 8h
                    Ngày 30/1- và 31/10: không có thời gian nghỉ do vào thứ 7 và chủ nhật, không có trong lich làm việc

                Tháng 11: có 2 ngày nghỉ từ 1/11 đến 2/11 , mỗi ngày 8h
        """

        self.create_leave(
            self.employee_A,
            self.unpaid_type,
            datetime(2021,10,28,8,0),
            datetime(2021,11,4,17,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-10-28 - Employee A
        domain = [
            ('date', '=', '2021-10-28'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-10-29 - Employee A
        domain = [
            ('date', '=', '2021-10-29'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-10-30,31  - Employee A
        domain = [
            ('date', '>=', '2021-10-30'),
            ('date', '<=', '2021-10-31'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)
        self.assertFalse(data)

        # 2021-11-1 - Employee A
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

        # 2021-11-2 - Employee A
        domain = [
            ('date', '=', '2021-11-2'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

    def test_report_5(self):
        """
        Nhân viên A:
            nghỉ có lương 2h ngày 1/11: từ 11h đến 13h
        Output:
            Báo cáo nghỉ:
                Ngày 1/11:
                    Nhân viên A : 1h
        """
        self.create_leave(
            self.employee_A,
            self.paid_type,
            datetime(2021,11,1,11,0),
            datetime(2021,11,1,13,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-11-1 - Employee A
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 1)
        self.assertEqual(data['duration_days'], 0.125)

    def test_report_6(self):
        """
        Nhân viên A:
            nghỉ có lương 2h ngày 1/11: từ 16h đến 18h
        Output:
            Báo cáo nghỉ:
                Ngày 1/11:
                    Nhân viên A : 1h
        """
        self.create_leave(
            self.employee_A,
            self.paid_type,
            datetime(2021,11,1,16,0),
            datetime(2021,11,1,18,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-11-1 - Employee A
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 1)
        self.assertEqual(data['duration_days'], 0.125)

    def test_report_7(self):
        """
        Nhân viên A:
            nghỉ có lương 2h ngày 1/11: từ 6h đến 9h
        Output:
            Báo cáo nghỉ:
                Ngày 1/11:
                    Nhân viên A : 1h
        """
        self.create_leave(
            self.employee_A,
            self.paid_type,
            datetime(2021,11,1,6,0),
            datetime(2021,11,1,9,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-11-1 - Employee A
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 1)
        self.assertEqual(data['duration_days'], 0.125)

    def test_report_8(self):
        """
        Nhân viên A:
            nghỉ có lương 12h ngày 1/11: từ 6h đến 18h
        Output:
            Báo cáo nghỉ:
                Ngày 1/11:
                    Nhân viên A : 8h
        """
        self.create_leave(
            self.employee_A,
            self.paid_type,
            datetime(2021,11,1,6,0),
            datetime(2021,11,1,18,0))

        fields = ['duration_days:sum', 'duration_hours:sum']
        groupby = ['employee_id','date:day']
        self.env['hr.leave.detail'].flush()

        # 2021-11-1 - Employee A
        domain = [
            ('date', '=', '2021-11-1'),
            ('employee_id', '=', self.employee_A.id)
        ]
        data = self.env['hr.leave.detail'].read_group(domain, fields, groupby, lazy=False)[0]
        self.assertEqual(data['duration_hours'], 8)
        self.assertEqual(data['duration_days'], 1)

    def test_check_timeoff_duration(self):
        """
        Nhân viên A:
            nghỉ có lương ngày 24/06: từ 8h đến 8h10
        Output:
            Cảnh báo thời gian nghỉ phải trên 30 phút
        """
        with self.assertRaises(UserError):
            self.create_leave(
                self.employee_A,
                self.paid_type,
                datetime(2021, 6, 24, 8, 0),
                datetime(2021, 6, 24, 8, 10))
