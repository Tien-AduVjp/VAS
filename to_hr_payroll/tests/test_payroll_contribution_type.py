from psycopg2 import IntegrityError

from odoo import fields
from odoo.tools import mute_logger
from odoo.tests import tagged
from odoo.exceptions import ValidationError, UserError

from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollContributionType(TestPayrollCommon):

    def create_wizard_change_rate(self, payroll_contribution_reg_ids, employee_contrib_rate, company_contrib_rate, date):
        return self.env['hr.payroll.contrib.action.change.rates'].create({
            'payroll_contribution_reg_ids': payroll_contribution_reg_ids.ids,
            'employee_contrib_rate':employee_contrib_rate,
            'company_contrib_rate':company_contrib_rate,
            'date': date
        })

    # 11A. Kiểu Đăng ký đóng góp từ lương
    def test_contribution_type_unique_code_1(self):
        """
        Case 1: Test trường Mã phải là duy nhất tương ứng với 1 công ty
            TH1: Khác mã => tạo thành công
        """
        register = self.env['hr.contribution.register'].search([('company_id', '=', self.env.company.id)], limit=1)
        type = self.env['hr.payroll.contribution.type'].create({
            'name': 'Type 1',
            'code': 'TT1',
            'employee_contrib_reg_id':register.id,
            'employee_contrib_rate': 1,
            'company_id': self.env.company.id
        })
        self.assertTrue(type, 'Test create payroll contribution type not oke')

    # 11A. Kiểu Đăng ký đóng góp từ lương
    def test_contribution_type_unique_code_2(self):
        """
        Case 1: Test trường Mã phải là duy nhất tương ứng với 1 công ty
            TH2: Cùng mã, khác công ty => Tạo thành công
        """
        ContributionType = self.env['hr.payroll.contribution.type']
        register = self.env['hr.contribution.register'].search([('company_id', '=', self.env.company.id)], limit=1)
        self.env['hr.payroll.contribution.type'].create({
            'name': 'Type 1',
            'code': 'TT1',
            'employee_contrib_reg_id':register.id,
            'employee_contrib_rate': 1,
            'company_id': self.env.company.id
        })

        company2 = self.env['res.company'].create({'name': 'CTY 2'})
        type = ContributionType.create({
            'name': 'Type 1',
            'code': 'TT1',
            'employee_contrib_reg_id':register.id,
            'employee_contrib_rate': 1,
            'company_id': company2.id
            })
        self.assertTrue(type, 'Test create payroll contribution type not oke')

    # 11A. Kiểu Đăng ký đóng góp từ lương
    @mute_logger('odoo.sql_db')
    def test_contribution_type_unique_code_3(self):
        """
        Case 1: Test trường Mã phải là duy nhất tương ứng với 1 công ty
            TH3: Cùng mã, cùng công ty => Tạo không thành công
        """
        register = self.env['hr.contribution.register'].search([('company_id', '=', self.env.company.id)], limit=1)
        ContributionType = self.env['hr.payroll.contribution.type']
        ContributionType.create({
            'name': 'Type 1',
            'code': 'TT1',
            'employee_contrib_reg_id':register.id,
            'employee_contrib_rate': 1,
            'company_id': self.env.company.id
            })

        with self.assertRaises(IntegrityError):
            ContributionType.create({
                'name': 'Type 2',
                'code': 'TT1',
                'employee_contrib_reg_id':register.id,
                'employee_contrib_rate': 1,
                'company_id': self.env.company.id
            })

    # 11A. Kiểu Đăng ký đóng góp từ lương
    def test_contribution_type_mass_change_rate(self):
        """
        Case 2: Test nút "Mass Change Rates"
            Output: Hiển thị form nhập thông tin thay đổi: ngày, tỷ lệ đóng góp của nhân viên, công ty

        Case 3: Test nút "Mass Change Rates", xác nhận thay đổi
            *with 6 states
            Output:
                Tất cả các đăng ký đóng góp từ lương liên quan đến loại này ở trạng thái "Đã xác nhận" / "Tái tham gia"  sẽ thay đổi tỷ lệ đóng góp của nhân viên và công ty
                Khi các đănng ký đóng góp từ lương này được thay đổi thì sẽ tạo ra các bản ghi lịch sử thay đổi đóng góp từ lương
                Kiểu đăng ký đóng góp sẽ không thay đổi tỷ lệ đóng góp
        """
        contrib_type = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=1)
        contrib_type.current_payroll_contribution_reg_ids.action_cancel()
        register_1 = self.create_contrib_register(self.product_emp_A, contrib_type, state="draft")

        # Case 2: Test button "Mass Change Rates"
        wizard_id = self.env.ref('to_hr_payroll.hr_payroll_contrib_action_change_rates_action').id
        result = contrib_type.action_mass_change_rates()
        self.assertEqual(wizard_id, result.get('id', False), "Test Wizard display: Change Contribution Rates not ok.")

        # Case 3: Test button "Mass Change Rates", Process change
        # TH1: State: Draft
        wizard_change_rate = self.create_wizard_change_rate(
            contrib_type.current_payroll_contribution_reg_ids,
            1, 2,
            fields.Date.today())
        wizard_change_rate.process()

        self.assertNotEqual(register_1.employee_contrib_rate, 1, 'Test Change Contribution Rates (with Draft state) not oke')
        self.assertNotEqual(register_1.company_contrib_rate, 2, 'Test Change Contribution Rates (with Draft state) not oke')
        self.assertFalse(register_1.payroll_contribution_history_ids, 'Test Change Contribution Rates (with Draft state) not oke')

        # TH2: State: Confirmed
        register_1.action_confirm()
        wizard_change_rate = self.create_wizard_change_rate(
            contrib_type.current_payroll_contribution_reg_ids,
            1, 2,
            fields.Date.from_string('2021-3-1'))
        wizard_change_rate.process()

        self.assertEqual(register_1.employee_contrib_rate, 1, 'Test Change Contribution Rates (with Confirmed state) not oke')
        self.assertEqual(register_1.company_contrib_rate, 2, 'Test Change Contribution Rates (with Confirmed state) not oke')
        self.assertEqual(
            register_1.payroll_contribution_history_ids[-1].date_from,
            fields.Date.from_string('2021-3-1'),
            'Test Change Contribution Rates (with Confirmed state) not oke')
        self.assertEqual(
            register_1.payroll_contribution_history_ids[-2].date_to,
            fields.Date.from_string('2021-2-28'),
            'Test Change Contribution Rates (with Confirmed state) not oke')

        # TH3: State: Suspended
        register_1.write({'date_suspended': fields.Date.from_string('2021-4-1')})
        register_1.with_context(call_wizard=False).action_suspend()
        wizard_change_rate = self.create_wizard_change_rate(
            contrib_type.current_payroll_contribution_reg_ids,
            3, 4,
            fields.Date.from_string('2021-5-1'))
        wizard_change_rate.process()

        self.assertNotEqual(register_1.employee_contrib_rate, 3, 'Test Change Contribution Rates (with suspended state) not oke')
        self.assertNotEqual(register_1.company_contrib_rate, 4, 'Test Change Contribution Rates (with suspended state) not oke')

        # TH4: State: Resumed
        register_1.write({'date_resumed': fields.Date.from_string('2021-4-30')})
        register_1.with_context(call_wizard=False).action_resume()
        wizard_change_rate = self.create_wizard_change_rate(
            contrib_type.current_payroll_contribution_reg_ids,
            3, 4,
            fields.Date.from_string('2021-5-1'))
        wizard_change_rate.process()

        self.assertEqual(register_1.employee_contrib_rate, 3, 'Test Change Contribution Rates (with resumed state) not oke')
        self.assertEqual(register_1.company_contrib_rate, 4, 'Test Change Contribution Rates (with resumed state) not oke')
        self.assertEqual(
            register_1.payroll_contribution_history_ids[-1].date_from,
            fields.Date.from_string('2021-5-1'),
            'Test Change Contribution Rates (with resumed state) not oke')

        # TH5: State: Done
        register_1.write({'date_to': fields.Date.from_string('2021-5-31')})
        register_1.with_context(call_wizard=False).action_done()
        wizard_change_rate = self.create_wizard_change_rate(
            contrib_type.current_payroll_contribution_reg_ids,
            5, 6,
            fields.Date.from_string('2021-5-1'))

        wizard_change_rate.process()
        self.assertNotEqual(register_1.employee_contrib_rate, 5, 'Test Change Contribution Rates (with Done state) not oke')
        self.assertNotEqual(register_1.company_contrib_rate, 6, 'Test Change Contribution Rates (with Done state) not oke')

        # TH6: State: Cancelled
        register_1.action_cancel()
        wizard_change_rate = self.create_wizard_change_rate(
            contrib_type.current_payroll_contribution_reg_ids,
            5, 6,
            fields.Date.from_string('2021-5-1'))
        wizard_change_rate.process()

        self.assertNotEqual(register_1.employee_contrib_rate, 5, 'Test Change Contribution Rates (with Cancelled state) not oke')
        self.assertNotEqual(register_1.company_contrib_rate, 6, 'Test Change Contribution Rates (with Cancelled state) not oke')

    # 11A. Kiểu Đăng ký đóng góp từ lương
    def test_contribution_type_mass_change_rate_2(self):
        """
        - 2 đăng ký đóng góp từ lương"
            - có cùng kiểu đăng ký đóng góp
            - có tỷ lệ đóng góp của nhân viên và công ty bằng nhau
        - Thay đổi tỷ lệ đóng góp của kiểu đóng góp này
            - vẫn bao gồm 2 kiểu đăng ký đóng góp từ lương ở bên trên

        => Thay đổi thành công
        """
        contrib_type = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=1)
        register_1 = self.create_contrib_register(
            self.product_emp_A,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=2,
            contrib_base=50000)
        register_2 = self.create_contrib_register(
            self.product_dep_manager,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=2,
            contrib_base=50000)
        (register_1 | register_2).action_confirm()

        wizard_change_rate = self.create_wizard_change_rate(
            contrib_type.current_payroll_contribution_reg_ids,
            1, 0,
            fields.Date.from_string('2021-8-1'))
        wizard_change_rate.process()

        self.assertRecordValues(
            register_1 | register_2,
            [{
                'employee_contrib_rate': 1,
                'company_contrib_rate': 0
            },
            {
                'employee_contrib_rate': 1,
                'company_contrib_rate': 0
            }])

    # 11A. Kiểu Đăng ký đóng góp từ lương
    def test_contribution_type_mass_change_rate_3(self):
        """
        - 2 đăng ký đóng góp từ lương"
            - có cùng kiểu đăng ký đóng góp
            - có tỷ lệ đóng góp của nhân viên bằng nhau
            - có tỷ lệ đóng góp của công ty khác nhau
        - Thay đổi tỷ lệ đóng góp của kiểu đóng góp này:
            - vẫn bao gồm 2 kiểu đăng ký đóng góp từ lương ở bên trên

        => Không thành công, Thông báo ngoại lệ
        """

        contrib_type = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=1)
        register_1 = self.create_contrib_register(
            self.product_emp_A,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=2,
            contrib_base=50000)
        register_2 = self.create_contrib_register(
            self.product_dep_manager,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=0,
            contrib_base=50000)
        (register_1 | register_2).action_confirm()

        with self.assertRaises(UserError):
            self.create_wizard_change_rate(
                contrib_type.current_payroll_contribution_reg_ids,
                1, 0,
                fields.Date.from_string('2021-8-1'))

    # 11A. Kiểu Đăng ký đóng góp từ lương
    def test_contribution_type_mass_change_rate_4(self):
        """
        - 2 đăng ký đóng góp từ lương"
            - có cùng kiểu đăng ký đóng góp
            - có tỷ lệ đóng góp của nhân viên khác nhau
            - có tỷ lệ đóng góp của công ty giống nhau
        - Thay đổi tỷ lệ đóng góp của kiểu đóng góp này:
            - vẫn bao gồm 2 kiểu đăng ký đóng góp từ lương ở bên trên

        => Không thành công, Thông báo ngoại lệ
        """
        contrib_type = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=1)
        register_1 = self.create_contrib_register(
            self.product_emp_A,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=2,
            company_rate=2,
            contrib_base=50000)
        register_2 = self.create_contrib_register(
            self.product_dep_manager,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=2,
            contrib_base=50000)
        (register_1 | register_2).action_confirm()

        with self.assertRaises(UserError):
            self.create_wizard_change_rate(
                contrib_type.current_payroll_contribution_reg_ids,
                3, 3,
                fields.Date.from_string('2021-8-1'))

    # 11A. Kiểu Đăng ký đóng góp từ lương
    def test_contribution_type_mass_change_rate_5(self):
        """
        - 2 đăng ký đóng góp từ lương"
            - có cùng kiểu đăng ký đóng góp
            - có tỷ lệ đóng góp của nhân viên giống nhau
            - có tỷ lệ đóng góp của công ty khác nhau
        - Thay đổi tỷ lệ đóng góp của kiểu đóng góp này:
            - Loại trừ đăng ký đóng góp có tỷ đóng góp khác nhau ra
            - chỉ còn các đăng ký đóng góp có tỷ lệ đóng góp giống nhau

        => Thành công
        """
        contrib_type = self.env['hr.payroll.contribution.type'].search([('company_id', '=', self.env.company.id)], limit=1)
        register_1 = self.create_contrib_register(
            self.product_emp_A,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=2,
            contrib_base=50000)
        register_2 = self.create_contrib_register(
            self.product_dep_manager,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=2,
            contrib_base=50000)
        employee_3 = self.create_employee('Employee 3')
        register_3 = self.create_contrib_register(
            employee_3,
            contrib_type,
            fields.Date.from_string('2021-7-1'),
            employee_rate=1,
            company_rate=2,
            contrib_base=50000)
        (register_1 | register_2 | register_3).action_confirm()

        wizard_change_rate = self.create_wizard_change_rate(
            (register_1 | register_2),
            1, 0,
            fields.Date.from_string('2021-8-1'))
        wizard_change_rate.process()

        self.assertRecordValues(
            register_1 | register_2 | register_3,
            [{
                'employee_contrib_rate': 1,
                'company_contrib_rate': 0
            },
            {
                'employee_contrib_rate': 1,
                'company_contrib_rate': 0
            },
            {
                'employee_contrib_rate': 1,
                'company_contrib_rate': 2
            }])
