from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestAccountMove(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccountMove, cls).setUpClass()

        # new Employee & Contract
        cls.product_emp_B = cls.create_employee(
            'Product Employee 1',
            job_id=cls.job_product_dev.id)
        cls.contract_emp_B = cls.create_contract(
            cls.product_emp_B.id,
            fields.Date.to_date('2021-01-01'),
            fields.Date.to_date('2021-12-31'),
            'open')

        # Contract Advantages
        TRAVEL_advantage = cls.env['hr.advantage.template'].search(
            [('company_id', '=', cls.env.company.id),
             ('code', '=', 'TRAVEL')])
        cls.contract_open_emp_A.write({
            'advantage_ids': [(0, 0, {'template_id': TRAVEL_advantage.id, 'amount': 1000000})]
        })
        cls.contract_emp_B.write({
            'advantage_ids': [(0, 0, {'template_id': TRAVEL_advantage.id, 'amount': 500000})]
        })

        # Rules
        cls.TRAVEL_rule = cls.env['hr.salary.rule'].search(
            [('company_id', '=', cls.env.company.id),
             ('code', '=', 'TRAVEL')])
        cls.TRAVEL_rule.write({
            'generate_account_move_line': True,
            'account_credit': cls.account_receivable.id
        })

    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-8-1'))
    def test_journal_entry_1(self):
        """
        Case 1: Test thông tin của bút toán sau khi tạo, tương ứng với từng phiếu lương
            Input: Bút toán của phiếu lương liên quan
                TH1: Ngày kế toán của phiếu lương > ngày hiện tại (ngày xác nhận phiếu lương)
            Output: Trường tham chiếu, sổ nhật ký, ngày kế toán giống với phiếu lương
                TH1: trường tự động vào sổ trên bút toán được đánh dấu, trạng thái dự thảo
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.write({'date': fields.Date.from_string('2021-8-5')})
        payslip.action_payslip_verify()

        self.assertRecordValues(
            payslip.move_id,
            [
                {
                    'date': payslip.date,
                    'journal_id': payslip.journal_id.id,
                    'ref': payslip.number,
                    'auto_post': True,
                    'state': 'draft',
                    }
                ]
            )

    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-8-1'))
    def test_journal_entry_2(self):
        """
        Case 1: Test thông tin của bút toán sau khi tạo, tương ứng với từng phiếu lương
            Input: Bút toán của phiếu lương liên quan
                TH2: Ngày kế toán của phiếu lương <= ngày hiện tại (ngày xác nhận phiếu lương)

            Output: Trường tham chiếu, sổ nhật ký, ngày kế toán giống với phiếu lương
                TH2: trường tự động vào sổ trên bút toán không được đánh dấu, trạng thái đã vào sổ
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.write({'date': fields.Date.from_string('2021-7-15')})
        payslip.action_payslip_verify()

        self.assertRecordValues(
            payslip.move_id,
            [
                {
                    'date': payslip.date,
                    'journal_id': payslip.journal_id.id,
                    'ref': payslip.number,
                    'auto_post': False,
                    'state': 'posted',
                    }
                ]
            )

    def test_employee_journal_item_01(self):
        """
        Test a salary rule not marked as `Force Encoding with Employee`

        Input:
            The company marked `Payslip Batch Journal Entry`
            The Salary rule marked `Generate Journal Item`:
                Marked Force Encoding with Employee
                Select Credit Account
            Payslip Batches with 2 payslips
        Output:
            There are 1 journal item line related to salary rule above
        """
        self.env.company.write({
            'payslip_batch_journal_entry': True,
            'general_employee_payable_account_id': self.account_payable.id
        })
        batch = self.create_payslip_run()
        payslip_emp_A = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.to_date('2021-07-01'),
            fields.Date.to_date('2021-07-31'),
            self.contract_open_emp_A.id)
        payslip_emp_B = self.create_payslip(
            self.product_emp_B.id,
            fields.Date.to_date('2021-07-01'),
            fields.Date.to_date('2021-07-31'),
            self.contract_emp_B.id)
        (payslip_emp_A | payslip_emp_B).write({'payslip_run_id': batch.id})
        (payslip_emp_A | payslip_emp_B).compute_sheet()
        batch.action_verify_payslips()

        move_line = batch.slip_ids.move_id.line_ids.filtered(lambda r:r.salary_rule_id==self.TRAVEL_rule)
        self.assertRecordValues(
            move_line,
            [{
                'account_id': self.account_receivable.id,
                'partner_id': False,
                'debit': 0.0,
                'credit': 1500000.0,
            }])

    def test_employee_journal_item_02(self):
        """
        Test a salary rule marked as `Force Encoding with Employee`

        Input:
            The company marked `Payslip Batch Journal Entry`
            The Salary rule marked `Generate Journal Item`:
                Marked Force Encoding with Employee
                Select Credit Account
            Payslip Batches with 2 payslips
        Output:
            There are 2 journal item lines related to salary rule above
        """
        self.TRAVEL_rule.employee_journal_item = True
        self.env.company.write({
            'payslip_batch_journal_entry': True,
            'general_employee_payable_account_id': self.account_payable.id
        })
        batch = self.create_payslip_run()
        payslip_emp_A = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.to_date('2021-07-01'),
            fields.Date.to_date('2021-07-31'),
            self.contract_open_emp_A.id)
        payslip_emp_B = self.create_payslip(
            self.product_emp_B.id,
            fields.Date.to_date('2021-07-01'),
            fields.Date.to_date('2021-07-31'),
            self.contract_emp_B.id)
        (payslip_emp_A | payslip_emp_B).write({'payslip_run_id': batch.id})
        (payslip_emp_A | payslip_emp_B).compute_sheet()
        batch.action_verify_payslips()

        move_lines = batch.slip_ids.move_id.line_ids.filtered(lambda r:r.salary_rule_id==self.TRAVEL_rule)
        self.assertRecordValues(
            move_lines,
            [{
                'account_id': self.account_receivable.id,
                'partner_id': self.product_emp_B.address_home_id.id,
                'debit': 0.0,
                'credit': 500000.0,
            },
            {
                'account_id': self.account_receivable.id,
                'partner_id': self.product_emp_A.address_home_id.id,
                'debit': 0.0,
                'credit': 1000000.0,
            }])
