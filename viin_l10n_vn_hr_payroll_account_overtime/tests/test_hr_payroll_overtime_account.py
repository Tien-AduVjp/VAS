from odoo import fields
from odoo.tools.date_utils import relativedelta

from odoo.tests.common import SavepointCase, tagged


@tagged('-at_install', 'post_install')
class TestHrPayrollOvertimeAccount(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHrPayrollOvertimeAccount, cls).setUpClass()

        cls.company_vn = cls.env['res.company'].sudo().search([('chart_template_id', '=', cls.env.ref('l10n_vn.vn_template').id)], limit=1)
        cls.env.company = cls.company_vn

        #Employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Employee Demo',
            'company_id': cls.company_vn.id,
        })

        #Salary structure
        cls.salary_structure = cls.env['hr.payroll.structure'].search(
            [('company_id', '=', cls.company_vn.id), ('code', '=', 'BASE')], limit=1
        )

        #Salary Cycle
        cls.salary_cycle_default = cls.env.ref('to_hr_payroll.hr_salary_cycle_default')

        #Contract
        cls.contract_employee = cls.env['hr.contract'].create({
            'name': 'Employee Demo',
            'employee_id': cls.employee.id,
            'company_id': cls.company_vn.id,
            'struct_id': cls.salary_structure.id,
            'date_start': '2021-10-10',
            'date_end': fields.Date.today() + relativedelta(days=100),
            'wage': 10000000,
        })
        cls.contract_employee.action_start_contract()

        #Overtime plan
        cls.overtime_plan_emp = cls.env['hr.overtime.plan'].create(
            {
                'employee_id': cls.employee.id,
                'reason_id':cls.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date': fields.Date.today() + relativedelta(days=5),
                'time_start': 19.0,
                'time_end': 21.0 ,
                'company_id': cls.company_vn.id
            })

    def test_01_hr_payroll_overtime_account(self):
        """
        Case 1: Kiểm tra quy tắc lương "Untaxed Overtime" (Mã: UNTAXED_OT) kích hoạt tạo phát sinh kế toán.
        """
        overtime_salary_rule = self.env['hr.salary.rule'].search([('code','=', 'UNTAXED_OT'), ('company_id', '=', self.company_vn.id)])
        self.assertRecordValues(
            overtime_salary_rule,
            [{'generate_account_move_line': True,
              'account_credit': self.env['account.account'].search([('code', '=', 334), ('company_id', '=', self.company_vn.id)], limit=1).id,
              'anylytic_option': 'debit_account'}]
        )

    def test_02_hr_payroll_overtime_account(self):
        """
        Case 3: Kiểm tra bút toán kế toán sinh ra sau khi xác nhận phiếu lương
        """
        #Payslip
        payslip_employee = self.env['hr.payslip'].create({
            'employee_id': self.employee.id,
            'contract_id' : self.contract_employee.id,
            'salary_cycle_id': self.salary_cycle_default.id,
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today() + relativedelta(days=31),
            'company_id': self.company_vn.id
        })
        payslip_employee.compute_sheet()
        self.assertTrue(payslip_employee.overtime_plan_line_ids)
        payslip_employee.action_payslip_verify()

        journal_entry_account_334 = payslip_employee.move_id.line_ids.filtered(
            lambda a: a.salary_rule_id.code == 'UNTAXED_OT' and a.account_id.code == '334'
        )
        self.assertTrue(journal_entry_account_334)
