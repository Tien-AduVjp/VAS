from odoo.tests.common import SavepointCase, tagged
from odoo import fields
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install', 'access_rights')
class TestSecurity(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSecurity, cls).setUpClass()
        cls.user = cls.env.ref('base.user_demo')
        cls.user.groups_id = [(6, 0, [cls.env.ref('base.group_user').id])]

    def test_01(self):
        """
            Người dùng của nhóm cán bộ bảng lương cũng có quyền của nhóm cán bộ tăng ca.
        """
        self.user.groups_id = [(4, self.env.ref('to_hr_payroll.group_hr_payroll_user').id, 0)]
        self.assertTrue(self.user.has_group('viin_hr_overtime.group_overtime_officer'))

    def test_02(self):
        """
            Người dùng nội bộ không có quyền bảng lương, tăng ca có thể nhìn thấy phiếu lương và dữ liệu tăng ca trên phiếu lương của mình.
        """
        contract = self.env.ref('hr_contract.hr_contract_qdp')
        contract.date_start = fields.date(2021, 3, 4)
        contract.action_start_contract()
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.user.employee_id.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 14),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.user.employee_id.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':fields.date(2021, 10, 1),
            'date_to':fields.date(2021, 10, 31),
            'company_id': self.user.employee_id.company_id.id or self.user.company_id.id,
            'contract_id':contract.id
        })
        payslip_01.compute_sheet()
        parent_user = self.user.copy()
        parent_user.groups_id = [(4, self.env.ref('to_hr_payroll.group_hr_payroll_team_leader').id, 0)]
        parent_user.action_create_employee()
        self.user.employee_id.parent_id = parent_user.employee_id.id
        self.assertTrue(payslip_01.with_user(parent_user).read())
        payslip_01.with_user(parent_user).overtime_plan_line_ids.read()
        self.assertTrue(payslip_01.with_user(self.user).read())
        self.assertTrue(payslip_01.with_user(self.user).overtime_plan_line_ids.read())
        # Ngưởi dùng trưởng nhóm bảng lương không có quyền tăng ca sẽ không thể xem được dòng tăng ca trên phiếu lương của nhân viên dưới quyền.
        with self.assertRaises(AccessError):
            payslip_01.with_user(parent_user).overtime_plan_line_ids.read()

    def test_03(self):
        """
            Ngưởi dùng của nhóm quản lý bảng lương cũng có quyền có nhóm cán bộ tăng ca.
        """
        self.user.groups_id = [(4, self.env.ref('to_hr_payroll.group_hr_payroll_manager').id, 0)]
        self.assertTrue(self.user.has_group('viin_hr_overtime.group_overtime_officer'))
