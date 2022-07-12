from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tests.common import SavepointCase, tagged, Form


@tagged('post_install', '-at_install')
class TestHRPayrollAttendance(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHRPayrollAttendance, cls).setUpClass()
        """"By default user demo has attendance from 1 last month to 10 last month,
            a attendance didn't have contract"""
        cls.user = cls.env.ref('base.user_demo')
        cls.partner = cls.user.partner_id
        cls.employee = cls.user.employee_id
        cls.employee.address_home_id = cls.partner
        cls.contract_employee_1 = cls.employee.contract_ids[0]
        # Need unlink all attendance from data demo
        cls.employee.attendance_ids.unlink()

        # Contracts
        cls.contract_employee_1.write({
            'date_start': datetime(2021, 1, 1),
            'date_end': datetime(2021, 8, 31),
            'state': 'draft',
            'salary_attendance_computation_mode': 'attendance',
            'salary_computation_mode': 'hour_basis'
        })
        cls.contract_employee_2 = cls.contract_employee_1.copy()
        cls.contract_employee_1.write({'state': 'open'})
        cls.contract_employee_2.write({
            'date_start': datetime(2021, 9, 2),
            'date_end': False,
        })
        cls.contract_employee_1.write({'state': 'open'})
        cls.contract_employee_2.write({'state': 'open'})

        # Attendances
        # Attendance 1: (T2), appear on payslip, total: 9h, valid_worked_hours: 8h
        cls.create_attendance(cls.employee.id, '2021-08-30 06:00:00', '2021-08-30 15:00:00')
        # Attendance 2: (T3), appear on payslip, total: 7h, valid_worked_hours: 6h, late_attendance_hours: 2h
        cls.create_attendance(cls.employee.id, '2021-08-31 08:00:00', '2021-08-31 15:00:00')
        # Attendance 3: (T6), appear on payslip, total: 7h, valid_worked_hours: 6h, early_leave_hours: 2h
        cls.create_attendance(cls.employee.id, '2021-08-27 06:00:00', '2021-08-27 13:00:00')
        # attendance 4: have no contract, does not appear on payslip
        cls.create_attendance(cls.employee.id, '2021-09-01 06:00:00', '2021-09-01 17:00:00')
        # Attendance 5: (T5), appear on payslip, total: 5h, valid_worked_hours: 4h, late_attendance_hours: 2h, early_leave_hours: 2h
        cls.create_attendance(cls.employee.id, '2021-09-02 08:00:00', '2021-09-02 13:00:00')
        # attendance 6: (T7), appear on payslip, total: 9h, valid_worked_hours: 0h
        cls.create_attendance(cls.employee.id, '2021-09-04 06:00:00', '2021-09-04 15:00:00')
        # attendance 7: (T6), appear on payslip, total: 9h, valid_worked_hours: 8h, missing check out
        cls.create_attendance(cls.employee.id, '2021-09-03 06:00:00', '2021-09-03 15:00:00', True)

        # Need to use Form test because: attendance_ids, attendance_count,total_attendance_hours... fields are computed
        # but store = False and not depend, Them are stored at caches
        cls.payslip_form = Form(cls.env['hr.payslip'])
        cls.payslip_form.employee_id = cls.user.employee_id
        cls.payslip_form.contract_id = cls.contract_employee_2
        cls.payslip_form.company_id = cls.env.company
        cls.payslip_form.date_from = datetime(2021, 8, 1)
        cls.payslip_form.date_to = datetime(2021, 10, 31)
        cls.payslip = cls.payslip_form.save()

    @classmethod
    def create_attendance(cls, employee_id, check_in, check_out=False, auto_checkout=False):
        return cls.env['hr.attendance'].with_context(tracking_disable=True).create({
            'employee_id': employee_id,
            'check_in': check_in,
            'check_out': check_out,
            'auto_checkout': auto_checkout
        })

    def test_1_attendance_infomation(self):
        """user Demo has attendance from 1 to 10 on this month"""
        # Test case 1
        self.assertRecordValues(
            self.payslip,
            [{
                'attendance_count': 6,
                'total_attendance_hours': 46,
                'valid_attendance_hours': 32,
                'late_attendance_count': 2,
                'late_attendance_hours': 4,
                'early_leave_count': 2,
                'early_leave_hours': 4,
                'missing_checkout_count': 1,
            }])

        # Test case 1.1, 4.1, 5.1
        # Attendance: (T5), appear on payslip, total: 9h, valid_worked_hours: 6h, late_attendance_hours: 2h
        self.create_attendance(self.employee.id, '2021-08-26 08:00:00', '2021-08-26 17:00:00')
        self.payslip = self.payslip_form.save()
        # recompute attendances as the compute method is not trigger when attendance is created after payslip creation.
        self.payslip.action_recompute_attendances()
        self.assertRecordValues(
            self.payslip,
            [{
                'attendance_count': 7,
                'total_attendance_hours': 55,
                'valid_attendance_hours': 38,
                'late_attendance_count': 3,
                'late_attendance_hours': 6,
                'early_leave_count': 2,
                'early_leave_hours': 4,
                'missing_checkout_count': 1,
            }])

    def test_3_payslip_batch(self):
        """Test case 3"""
        payslip_batch_form = Form(self.env['hr.payslip.run'])
        payslip_batch_form.date_start = (
            datetime.now() + relativedelta(months=-2)).strftime('%Y-%m-01')
        payslip_batch_form.date_end = datetime.now() + relativedelta(months=-1, day=31)
        user_admin = self.env.ref('base.user_admin')
        with payslip_batch_form.slip_ids.new() as line_form:
            line_form.employee_id = self.user.employee_id
            line_form.contract_id = self.contract_employee_2
            line_form.company_id = self.env.company
            line_form.date_from = datetime(2021, 8, 30)
            line_form.date_to = datetime(2021, 10, 31)
        user_admin.employee_id.address_home_id = user_admin.partner_id
        contract = user_admin.employee_id.contract_ids[0]
        contract.write({
            'date_start': datetime(2020, 8, 30),
            'date_end': False,
            'state': 'open'
        })
        # Need unlink all attendance from data demo
        user_admin.employee_id.attendance_ids.unlink()
        self.env['hr.attendance'].create({
            'employee_id': user_admin.employee_id.id,
            'check_in':datetime(2021, 9, 6, 8),
            'check_out':datetime(2021, 9, 6, 15),
            })
        with payslip_batch_form.slip_ids.new() as line_form:
            line_form.employee_id = user_admin.employee_id
            line_form.contract_id = contract
            line_form.company_id = self.env.company
            line_form.date_from = datetime(2021, 8, 30)
            line_form.date_to = datetime(2021, 10, 31)
        payslip_batch = payslip_batch_form.save()

        self.assertEqual(len(payslip_batch.attendance_ids), 7,
                         "to_hr_payroll_attendance: hr.payslip.run, Error compute attendance")

    def test_4_hr_working_month_calendar(self):
        working_month_september = self.payslip.working_month_calendar_ids[1]
        september_lines = working_month_september.line_ids
        self.assertRecordValues(
            working_month_september,
            [{
                'attendance_count': 3,
                'total_attendance_hours': 23,
                'valid_attendance_hours': 12,
                'late_attendance_count': 1,
                'late_attendance_hours': 2,
                'early_leave_count': 1,
                'early_leave_hours': 2,
                'missing_checkout_count': 1,
                'paid_rate': 0.06818181818181818 # 12/176
            }])
        self.assertRecordValues(
            september_lines,
            [{
                'contract_id': False,
                'date_from': date(2021, 9, 1),
                'date_to': date(2021, 9, 1),
                'total_attendance_hours': 0,
                'valid_attendance_hours': 0,
                'late_attendance_count': 0,
                'late_attendance_hours': 0,
                'early_leave_count': 0,
                'early_leave_hours': 0,
                'missing_checkout_count': 0,
                'paid_rate': 0
            },
            {
                'contract_id': self.contract_employee_2.id,
                'date_from': date(2021, 9, 2),
                'date_to': date(2021, 9, 30),
                'total_attendance_hours': 23,
                'valid_attendance_hours': 12,
                'late_attendance_count': 1,
                'late_attendance_hours': 2,
                'early_leave_count': 1,
                'early_leave_hours': 2,
                'missing_checkout_count': 1,
                'paid_rate': 0.06818181818181818 # 12/176
            }])

        working_month_august = self.payslip.working_month_calendar_ids[0]
        self.assertRecordValues(
            working_month_august,
            [{
                'attendance_count': 3,
                'total_attendance_hours': 23,
                'valid_attendance_hours': 20,
                'late_attendance_count': 1,
                'late_attendance_hours': 2,
                'early_leave_count': 1,
                'early_leave_hours': 2,
                'missing_checkout_count': 0,
                'paid_rate': 0.11363636363636363 # 20/176
            }])
        self.assertRecordValues(
            working_month_august.line_ids,
            [{
                'contract_id': self.contract_employee_1.id,
                'date_from': date(2021, 8, 1),
                'date_to': date(2021, 8, 31),
                'total_attendance_hours': 23,
                'valid_attendance_hours': 20,
                'late_attendance_count': 1,
                'late_attendance_hours': 2,
                'early_leave_count': 1,
                'early_leave_hours': 2,
                'missing_checkout_count': 0,
                'paid_rate': 0.11363636363636363 # 20/176
            }])
