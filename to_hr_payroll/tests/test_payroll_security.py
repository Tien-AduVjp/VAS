from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import tagged
from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollSecurity(TestPayrollCommon):

    def setUp(self):
        super(TestPayrollSecurity, self).setUp()

        # group user
        group_internal = self.env.ref('base.group_user')
        group_team_leader = self.env.ref('to_hr_payroll.group_hr_payroll_team_leader')
        group_payroll_user = self.env.ref('to_hr_payroll.group_hr_payroll_user')
        group_payroll_manager = self.env.ref('to_hr_payroll.group_hr_payroll_manager')

        # User - employee
        groups_ids = [group_internal.id, group_team_leader.id]
        self.leader_user = self.create_user('Leader User', 'leader_user', 'leader_user', groups_ids)
        self.leader_user.action_create_employee()
        self.leader_employee = self.leader_user.employee_id

        groups_ids = [group_internal.id, group_payroll_user.id]
        self.officer_user = self.create_user('Officer User', 'officer_user', 'officer_user', groups_ids)
        self.officer_user.action_create_employee()
        self.officer_employee = self.officer_user.employee_id

        groups_ids = [group_internal.id, group_payroll_manager.id]
        self.manager_user = self.create_user('Manager User', 'manager_user', 'manager_user', groups_ids)
        self.manager_user.action_create_employee()
        self.manager_employee = self.manager_user.employee_id

        groups_ids = [group_internal.id]
        self.product_user_1 = self.create_user('Product Employee 1', 'product_employee1', 'product_employee1', groups_ids)
        self.product_user_1.action_create_employee()
        self.product_employee_1 = self.product_user_1.employee_id

        self.product_user_2 = self.create_user('Product Employee 2', 'product_employee2', 'product_employee2', groups_ids)
        self.product_user_2.action_create_employee()
        self.product_employee_2 = self.product_user_2.employee_id

        self.product_department_user = self.create_user(
            'Product Department Manager',
            'product_department_user',
            'product_department_user',
            groups_ids)

        self.contract_employee_1 = self.create_contract(
            self.product_employee_1.id,
            fields.Date.from_string('2021-1-1'),
            wage=35000000)
        self.contract_employee_2 = self.create_contract(
            self.product_employee_2.id,
            fields.Date.from_string('2021-1-1'),
            wage=35000000)
        self.contract_team_leader = self.create_contract(
            self.leader_employee.id,
            fields.Date.from_string('2021-1-1'),
            wage=35000000)
        self.contract_officer_employee = self.create_contract(
            self.officer_employee.id,
            fields.Date.from_string('2021-1-1'),
            wage=35000000)

    def test_payroll_security_internal_user_1(self):
        """
        1. Người dùng nội bộ
            Case 1: Check quyền truy cập của người dùng nội bộ (Access Rights)
                TH1: Check quyền truy cập model Payslip
                TH2: Check quyền truy cập model Payslip Personal Income Tax Analysis
                TH3: Check quyền truy cập model Payroll Analysis
                TH4: Check quyền truy cập model Payroll Contribution Analysis
        """
        # TH1: Check quyền truy cập model Payslip (Access Rights)
        Payslip = self.env['hr.payslip'].with_user(self.product_user_1)
        self.assertTrue(Payslip.check_access_rights('read'), 'Test Access Right (Payslip) for internal user not oke')
        self.assertRaises(AccessError, Payslip.check_access_rights, 'create')
        self.assertRaises(AccessError, Payslip.check_access_rights, 'write')
        self.assertRaises(AccessError, Payslip.check_access_rights, 'unlink')

        # TH2: Check quyền truy cập model Payslip Personal Income Tax Analysis
        TaxAnalysis = self.env['payslip.personal.income.tax.analysis'].with_user(self.product_user_1)
        self.assertTrue(TaxAnalysis.check_access_rights('read'), 'Test Access Right (Payslip) for internal user not oke')

        # TH3: Check quyền truy cập model Payroll Analysis
        PayrollAnalysis = self.env['hr.payroll.analysis'].with_user(self.product_user_1)
        self.assertRaises(AccessError, PayrollAnalysis.check_access_rights, 'read')

    def test_payroll_security_internal_user_2(self):
        """
        1. Người dùng nội bộ
            Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
                TH1: Phiếu lương của chính mình
                TH2: Phiếu lương của người khác
        """
        # Prepare data for test access rule
        payslip_1 = self.create_payslip(
            self.product_employee_1.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_employee_1.id)

        payslip_2 = self.create_payslip(
            self.product_employee_2.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_employee_2.id)

        # TH1: Phiếu lương của chính mình
        self.assertIsNone(payslip_1.with_user(
            self.product_user_1).check_access_rule('read'),
            'Test access rule (Payslip) for internal user not oke')

        # TH2: Phiếu lương của người khác
        self.assertRaises(AccessError, payslip_2.with_user(self.product_user_1).check_access_rule, 'read')

        """
        1. Người dùng nội bộ
            Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
                Output: Xem báo cáo phân tích thuế TNCN của chính mình
        """
        payslip_1.compute_sheet()
        payslip_2.compute_sheet()
        taxs = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_1_taxs = taxs.filtered(lambda r:r.employee_id == self.product_employee_1)
        employee_2_taxs = taxs.filtered(lambda r:r.employee_id == self.product_employee_2)

        # Xem bản ghi báo cáo thuế của chính mình
        self.assertIsNone(
            employee_1_taxs.with_user(self.product_user_1).check_access_rule('read'),
            'Test access rule (Payslip Personal Income Tax Analysis) for internal user not oke')

        # Xem bản ghi báo cáo thuế của người khác
        self.assertRaises(AccessError, employee_2_taxs.with_user(self.product_user_1).check_access_rule, 'read')

    # 2. Người dùng trưởng nhóm
    def test_payroll_security_team_leader_1(self):
        """
        1. Người dùng trưởng nhóm
            Case 1: Check quyền truy cập của người dùng trưởng nhóm (Access Rights)
                TH1: Check quyền truy cập model Payslip
                TH2: Check quyền truy cập model Payslip Personal Income Tax Analysis
                TH3: Check quyền truy cập model Payroll Analysis
                TH4: Check quyền truy cập model Payroll Contribution Analysis
        """
        # TH1: Check quyền truy cập model Payslip
        Payslip = self.env['hr.payslip'].with_user(self.leader_user)
        self.assertTrue(Payslip.check_access_rights('read'), 'Test Access Right (Payslip) for team leader not oke')
        self.assertRaises(AccessError, Payslip.check_access_rights, 'create')
        self.assertRaises(AccessError, Payslip.check_access_rights, 'write')
        self.assertRaises(AccessError, Payslip.check_access_rights, 'unlink')

        # TH2: Check quyền truy cập model Payslip Personal Income Tax Analysis
        TaxAnalysis = self.env['payslip.personal.income.tax.analysis'].with_user(self.leader_user)
        self.assertTrue(TaxAnalysis.check_access_rights('read'), 'Test Access Right (Payslip) for team leader not oke')

        # TH3: Check quyền truy cập model Payroll Analysis
        PayrollAnalysis = self.env['hr.payroll.analysis'].with_user(self.leader_user)
        self.assertTrue(
            PayrollAnalysis.check_access_rights('read'),
            'Test Access Right (Payroll Analysis) for team leader user not oke')

    # 2. Người dùng trưởng nhóm
    def test_payroll_security_team_leader_2(self):
        """
        Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
            TH1: Phiếu lương của chính mình
                Output: Thành công
        """
        payslip = self.create_payslip(
            self.leader_employee.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_team_leader.id)
        self.assertIsNone(
            payslip.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payslip) for team leader not oke')

        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH1: Xem báo cáo phân tích thuế của chính mình
                Output: Thành công
        """
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        leader_employee_taxs = lines.filtered(lambda r:r.employee_id == self.leader_employee)
        self.assertIsNone(
            leader_employee_taxs.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payslip Personal Income Tax Analysis) for team leader not oke')

        """
        Case 4: Check quyền truy cập  bản ghi Payroll Analysis (Access Rules)
            TH1: Xem báo cáo phân tích lương của chính mình
                Output: Thành công
        """
        lines = self.env['hr.payroll.analysis'].search([('company_id', '=', self.env.company.id)])
        leader_employee_lines = lines.filtered(lambda r:r.employee_id == self.leader_employee)
        self.assertIsNone(
            leader_employee_lines.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payroll Analysis) for team leader not oke')

    def test_payroll_security_team_leader_3(self):
        """
        1. Người dùng trưởng nhóm
            Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
                TH2: Phiếu lương của nhân viên cấp dưới
        """
        self.product_employee_2.write({'parent_id': self.leader_employee.id})
        payslip = self.create_payslip(
            self.product_employee_2.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_employee_2.id)

        self.assertIsNone(
            payslip.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payslip) for team leader not oke')

        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH2: Xem báo cáo phân tích thuế của nhân viên cấp dưới
                Output: Thành công
        """
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_taxs = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            employee_2_taxs.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payslip Personal Income Tax Analysis) for team leader not oke')

        """
        Case 4: Check quyền truy cập  bản ghi Payroll Analysis (Access Rules)
            TH2: Xem báo cáo phân tích lương của cấp dưới
                Output: Thành công
        """
        lines = self.env['hr.payroll.analysis'].search([('company_id', '=', self.env.company.id)])
        leader_employee_lines = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            leader_employee_lines.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payroll Analysis) for team leader not oke')

    def test_payroll_security_team_leader_4(self):
        """
        1. Người dùng trưởng nhóm
            Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
                TH3: Phiếu lương của nhân viên thuộc phòng ban mình quản lý
        """
        self.product_employee_2.write({
            'department_id': self.product_department.id,
            'parent_id': False
        })
        self.product_department.write({
            'manager_id': self.leader_employee.id
        })
        payslip = self.create_payslip(
            self.product_employee_2.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_employee_2.id)
        self.assertIsNone(
            payslip.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payslip) for team leader not oke')

        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH3: Xem báo cáo phân tích thuế của nhân viên thuộc phòng ban mình quản lý
                Output: Thành công
        """
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_taxs = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            employee_2_taxs.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payslip Personal Income Tax Analysis) for team leader not oke')

        """
        Case 4: Check quyền truy cập  bản ghi Payroll Analysis (Access Rules)
            TH3: Xem báo cáo phân tích lương của nhân viên thuộc phòng ban mình quản lý
                Output: Thành công
        """
        lines = self.env['hr.payroll.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_lines = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            employee_2_lines.with_user(self.leader_user).check_access_rule('read'),
            'Test access rule (Payroll Analysis) for team leader not oke')

    def test_payroll_security_team_leader_5(self):
        """
        1. Người dùng trưởng nhóm
            Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
                TH4: Phiếu lương của người khác, không thuộc TH2,3
        """
        payslip = self.create_payslip(
            self.product_employee_2.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_employee_2.id)
        self.assertRaises(AccessError, payslip.with_user(self.leader_user).check_access_rule, 'read')

        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH4: Xem báo cáo phân tích thuế của người khác
                    (Không phải là nhân viên cấp dưới, thuộc phòng ban mình quản lý)
                Output: Không thành công
        """
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_taxs = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertRaises(AccessError, employee_2_taxs.with_user(self.leader_user).check_access_rule, 'read')

# #         """
# #         Case 4: Check quyền truy cập  bản ghi Payroll Analysis (Access Rules)
# #             TH4: Xem báo cáo phân tích thuế của người khác
# #                     (Không phải là nhân viên cấp dưới, thuộc phòng ban mình quản lý)
# #                 Output: Không thành công
# #         """
# #         lines = self.env['hr.payroll.analysis'].search([('company_id', '=', self.env.company.id)])
# #         employee_2_lines = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
# #         self.assertRaises(AccessError, employee_2_lines.with_user(self.leader_user).check_access_rule, 'read')

    def test_payroll_security_officer_0(self):
        """
        1. Người dùng cán bộ
            Case 0: Có quyền Officer (hr.group_hr_user) của HR
        """
        self.assertTrue(self.officer_user.has_group('hr.group_hr_user'), 'Test Officer (hr.group_hr_user) not oke')
        self.assertTrue(
            self.officer_user.has_group('to_hr_payroll.group_hr_payroll_team_leader'),
            'Test Officer (hr.group_hr_user) not oke')

    def test_payroll_security_officer_1(self):
        """
        3. Người dùng cán bộ
            Case 1: Check quyền truy cập của người dùng trưởng nhóm (Access Rights)
                TH1: Check quyền truy cập model Payslip
                TH2: Check quyền truy cập model Payslip Personal Income Tax Analysis
                TH3: Check quyền truy cập model Payroll Analysis
                TH4: Check quyền truy cập model Payroll Contribution Analysis
        """
        # TH1: Check quyền truy cập model Payslip
        Payslip = self.env['hr.payslip'].with_user(self.officer_user)
        self.assertTrue(Payslip.check_access_rights('read'), 'Test Access Right (Payslip) for officer not oke')
        self.assertTrue(Payslip.check_access_rights('create'), 'Test Access Right (Payslip) for officer not oke')
        self.assertTrue(Payslip.check_access_rights('write'), 'Test Access Right (Payslip) for officer not oke')
        self.assertTrue(Payslip.check_access_rights('unlink'), 'Test Access Right (Payslip) for officer not oke')

        # TH2: Check quyền truy cập model Payslip Personal Income Tax Analysis
        TaxAnalysis = self.env['payslip.personal.income.tax.analysis'].with_user(self.officer_user)
        self.assertTrue(TaxAnalysis.check_access_rights('read'), 'Test Access Right (Payslip) for officer not oke')

        # TH3: Check quyền truy cập model Payroll Analysis
        PayrollAnalysis = self.env['hr.payroll.analysis'].with_user(self.officer_user)
        self.assertTrue(PayrollAnalysis.check_access_rights('read'),'Test Access Right (Payroll Analysis) for officer not oke')

    # 3. Người dùng cán bộ
    def test_payroll_security_officer_2(self):
        """
        Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
            TH1: Phiếu lương của chính mình
                Output: không có quyền sửa xóa phiếu lương của chính mình
        """
        payslip = self.create_payslip(
            self.officer_employee.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_officer_employee.id)
        self.assertIsNone(
            payslip.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payslip) for officer not oke'
            )
        self.assertIsNone(payslip.with_user(self.officer_user).check_access_rule('write'), )
        self.assertIsNone(payslip.with_user(self.officer_user).check_access_rule('unlink'), )

        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH1: Xem báo cáo phân tích thuế của chính mình
                Output: Thành công
        """
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        leader_employee_taxs = lines.filtered(lambda r:r.employee_id == self.officer_employee)
        self.assertIsNone(
            leader_employee_taxs.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payslip Personal Income Tax Analysis) for officer not oke')

        """
        Case 4: Check quyền truy cập  bản ghi Payroll Analysis (Access Rules)
            TH1: Xem báo cáo phân tích lương của chính mình
                Output: Thành công
        """
        lines = self.env['hr.payroll.analysis'].search([('company_id', '=', self.env.company.id)])
        leader_employee_lines = lines.filtered(lambda r:r.employee_id == self.officer_employee)
        self.assertIsNone(
            leader_employee_lines.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payroll Analysis) for officer not oke')

    # 3. Người dùng cán bộ
    def test_payroll_security_officer_3A(self):
        """
        Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
            TH2: Phiếu lương của nhân viên cấp dưới
                Output: Full quyền
        """
        self.product_employee_2.write({'parent_id': self.officer_employee.id})
        payslip = self.env['hr.payslip'].with_user(self.officer_user).create({
            'employee_id': self.product_employee_2.id,
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_employee_2.id,
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
            'company_id': self.env.company.id
        })
        self.assertIsNone(
            payslip.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payslip) for officer not oke')
        self.assertIsNone(
            payslip.with_user(self.officer_user).check_access_rule('write'),
            'Test access rule (Payslip) for officer not oke')
        self.assertIsNone(
            payslip.with_user(self.officer_user).check_access_rule('unlink'),
            'Test access rule (Payslip) for officer not oke')

    # 3. Người dùng cán bộ
    def test_payroll_security_officer_3B(self):
        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH2: Xem báo cáo phân tích thuế của nhân viên cấp dưới
                Output: Thành công
        """
        self.product_employee_2.write({'parent_id': self.officer_employee.id})
        payslip = self.env['hr.payslip'].create({
            'employee_id': self.product_employee_2.id,
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_employee_2.id,
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
            'company_id': self.env.company.id
        })
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_taxs = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            employee_2_taxs.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payslip Personal Income Tax Analysis) for officer not oke')

    # 3. Người dùng cán bộ
    def test_payroll_security_officer_3C(self):
        """
        Case 4: Check quyền truy cập  bản ghi Payroll Analysis (Access Rules)
            TH2: Xem báo cáo phân tích lương của cấp dưới
                Output: Thành công
        """
        self.product_employee_2.write({'parent_id': self.officer_employee.id})
        payslip = self.env['hr.payslip'].create({
            'employee_id': self.product_employee_2.id,
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_employee_2.id,
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
            'company_id': self.env.company.id
        })
        payslip.compute_sheet()
        lines = self.env['hr.payroll.analysis'].search([('company_id', '=', self.env.company.id)])
        leader_employee_lines = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            leader_employee_lines.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payroll Analysis) for officer not oke')


    # 3. Người dùng cán bộ
    def test_payroll_security_officer_4(self):
        """
        Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
            TH3: Phiếu lương của nhân viên thuộc phòng ban mình quản lý
                Output: Full quyền
        """
        self.product_employee_2.write({
            'department_id': self.product_department.id,
            'parent_id': False
        })
        self.product_department.write({
            'manager_id': self.officer_employee.id
        })

        payslip = self.env['hr.payslip'].with_user(self.officer_user).create({
            'employee_id': self.product_employee_2.id,
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_employee_2.id,
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
            'company_id': self.env.company.id
        })
        self.assertIsNone(
            payslip.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payslip) for officer not oke')
        self.assertIsNone(
            payslip.with_user(self.officer_user).check_access_rule('write'),
            'Test access rule (Payslip) for officer not oke')
        self.assertIsNone(
            payslip.with_user(self.officer_user).check_access_rule('unlink'),
            'Test access rule (Payslip) for officer not oke')

        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH3: Xem báo cáo phân tích thuế của nhân viên thuộc phòng ban mình quản lý
                Output: Thành công
        """
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_taxs = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            employee_2_taxs.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payslip Personal Income Tax Analysis) for officer not oke')

        """
        Case 4: Check quyền truy cập  bản ghi Payroll Analysis (Access Rules)
            TH3: Xem báo cáo phân tích lương của nhân viên thuộc phòng ban mình quản lý
                Output: Thành công
        """
        lines = self.env['hr.payroll.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_lines = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(
            employee_2_lines.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Payroll Analysis) for officer not oke')

    # 3. Người dùng cán bộ
    def test_payroll_security_officer_5(self):
        """
        Case 2: Check quyền truy cập bản ghi Payslip (Access Rules)
            TH4: Phiếu lương của người khác, không thuộc TH2,3
        """
        payslip = self.create_payslip(
            self.product_employee_2.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_employee_2.id)
        self.assertIsNone(payslip.with_user(self.officer_user).check_access_rule('read'))
        self.assertIsNone(payslip.with_user(self.officer_user).check_access_rule('write'))
        self.assertIsNone(payslip.with_user(self.officer_user).check_access_rule('unlink'))

        """
        Case 3: Check quyền truy cập  bản ghi Payslip Personal Income Tax Analysis (Access Rules)
            TH4: Xem báo cáo phân tích thuế của người khác
                    (Không phải là nhân viên cấp dưới, không thuộc phòng ban mình quản lý)
                Output: Không thành công
        """
        payslip.compute_sheet()
        lines = self.env['payslip.personal.income.tax.analysis'].search([('company_id', '=', self.env.company.id)])
        employee_2_taxs = lines.filtered(lambda r:r.employee_id == self.product_employee_2)
        self.assertIsNone(employee_2_taxs.with_user(self.officer_user).check_access_rule('read'))

    def test_payroll_security_officer_6(self):
        """
        1. Người dùng cán bộ
            Case 3: Xem hợp đồng nhân viên cấp dưới/thuộc phòng ban quản lý
                TH1.1: Hợp đồng của chính mình - không phải là trưởng phòng
                    # k xem được hợp đồng
                TH1.2: Hợp đồng của chính mình - là trưởng phòng
                    # xem được hợp đồng
        """
        # TH1.1: Hợp đồng của chính mình - không phải là trưởng phòng
        self.assertIsNone(self.contract_officer_employee.with_user(self.officer_user).check_access_rule('read'))

        # TH1.2: Hợp đồng của chính mình - là trưởng phòng
        self.officer_user.write({
            'department_id': self.product_department.id,
        })
        self.product_department.write({
            'manager_id': self.officer_employee.id
        })
        self.assertIsNone(
            self.contract_officer_employee.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Contracts) for officer not oke')

    def test_payroll_security_officer_7(self):
        """
        1. Người dùng cán bộ
            Case 3: Xem hợp đồng nhân viên cấp dưới/thuộc phòng ban quản lý
                TH2: Hợp đồng của nhân viên cấp dưới
                    # xem được hợp đồng
        """
        self.product_employee_2.write({
            'parent_id': self.officer_employee.id
        })
        self.assertIsNone(
            self.contract_employee_2.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Contracts) for officer not oke')

    def test_payroll_security_officer_8(self):
        """
        1. Người dùng cán bộ
            Case 3: Xem hợp đồng nhân viên cấp dưới/thuộc phòng ban quản lý
                TH3: Hợp đồng của nhân viên thuộc phòng ban mình quản lý
                    # xem được hợp đồng
        """
        self.product_employee_2.write({
            'department_id': self.product_department.id,
            'parent_id': False
        })
        self.product_department.write({
            'manager_id': self.officer_employee.id
        })
        self.assertIsNone(
            self.contract_employee_2.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Contracts) for officer not oke')

    def test_payroll_security_officer_9(self):
        """
        1. Người dùng cán bộ
            Case 3: Xem hợp đồng nhân viên cấp dưới/thuộc phòng ban quản lý
                TH4: Hợp đồng của người khác, không thuộc TH2,3
                    # không xem được hợp đồng
        """
        self.assertRaises(AccessError, self.contract_employee_2.with_user(self.officer_user).check_access_rule('read'))

    def test_payroll_security_officer_10(self):
        """
        3. Người dùng cán bộ
            Case 4: Full quyền với đăng ký đóng góp từ lương
        """
        type = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=1)
        ContribRegister = self.env['hr.payroll.contribution.register']
        register = ContribRegister.with_user(self.officer_user).create({
            'employee_id': self.manager_employee.id,
            'type_id': type.id,
            'date_from': fields.Date.from_string('2021-1-1'),
            'state': 'draft',
            'computation_method': type.computation_method,
            'employee_contrib_rate': 1,
            'company_contrib_rate': 1,
            'contribution_base': 5000
        })
        self.assertTrue(register, 'Test access rule (Contribution Register) for officer not oke')
        self.assertIsNone(
            register.with_user(self.officer_user).check_access_rule('read'),
            'Test access rule (Contribution Register) for officer not oke')
        self.assertIsNone(
            register.with_user(self.officer_user).check_access_rule('write'),
            'Test access rule (Contribution Register) for officer not oke')
        self.assertIsNone(
            register.with_user(self.officer_user).check_access_rule('unlink'),
            'Test access rule (Contribution Register) for officer not oke')

    def test_payroll_security_manager_0(self):
        """
        1. Người dùng quản lý
            Case 0: Có quyền Administrator (hr_contract.group_hr_contract_manager) của HR Contract
        """
        self.assertTrue(
            self.manager_user.has_group('hr_contract.group_hr_contract_manager'),
            'Test Contract Manager (hr_contract.group_hr_contract_manager) not oke')
        self.assertTrue(
            self.manager_user.has_group('to_hr_payroll.group_hr_payroll_user'),
            'Test Contract Manager (hr.group_hr_user) not oke')

    # ...
