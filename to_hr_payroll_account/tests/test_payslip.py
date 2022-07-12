from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import Form

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestPayslip(TestCommon):

    def test_form_payslip_1(self):
        """
        Case 1: Test trường Sổ nhật ký lương mặc định / khi thay đổi hợp đồng
            TH1: Không có hợp đồng
                Output: Sổ nhật ký mặc định là sổ nhật ký "Lương nhân viên", mã là "SAL"
        """
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'SAL')
            ], limit = 1)
        f = Form(self.env['hr.payslip'])
        self.assertEqual(f.journal_id, journal, 'Test default field: journal_id not oke')

    def test_form_payslip_2(self):
        """
        Case 1: Test trường Sổ nhật ký lương mặc định / khi thay đổi hợp đồng
            TH2: có hợp đồng, hợp đồng không có sổ nhật ký lương
                Output: Sổ nhật ký mặc định là sổ nhật ký "Lương nhân viên", mã là "SAL"
        """
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'SAL')
            ], limit = 1)
        contract = self.env['hr.contract'].search([('company_id', '=', self.env.company.id)], limit = 1)
        contract.write({'journal_id': False})

        f = Form(self.env['hr.payslip'])
        f.contract_id = contract
        self.assertEqual(f.journal_id, journal, 'Test default field: journal_id not oke')

    def test_form_payslip_3(self):
        """
        Case 1: Test trường Sổ nhật ký lương mặc định / khi thay đổi hợp đồng
            TH3: có hợp đồng, hợp đồng có sổ nhật ký lương
                Output: Sổ nhật ký là sổ nhật ký trên hợp đồng
        """
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '!=', 'SAL')
            ], limit = 1)
        contract = self.env['hr.contract'].search([('company_id', '=', self.env.company.id)], limit = 1)
        contract.write({'journal_id': journal})

        f = Form(self.env['hr.payslip'])
        f.contract_id = contract
        self.assertEqual(f.journal_id, journal, 'Test default field: journal_id not oke')

    def test_private_address_alert_1(self):
        """
        Case 1: Test cảnh báo trên phiếu lương khi tạo phiếu lương nhân viên không có địa chỉ riêng tư
            Input: Tạo phiếu lương của nhân viên không có địa chỉ riêng tư
            Output: Cảnh báo "Không có địa chỉ riêng tư thiết lập cho nhân viên X. 
                Vì vậy, các bút toán kế toán tạo ra bởi phiếu lương này sẽ không liên kết đến bất kỳ ai."
        """
        self.product_emp_A.write({'address_home_id': False})
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )

        self.assertTrue(payslip.non_private_address_alert)

    def test_private_address_alert_2(self):
        """
        Case 1: Test cảnh báo trên phiếu lương khi tạo phiếu lương nhân viên không có địa chỉ riêng tư
            Input: Tạo phiếu lương của nhân viên không có địa chỉ riêng tư
            Output: Cảnh báo "Không có địa chỉ riêng tư thiết lập cho nhân viên X. 
                Vì vậy, các bút toán kế toán tạo ra bởi phiếu lương này sẽ không liên kết đến bất kỳ ai."
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        self.assertFalse(payslip.non_private_address_alert)

    def test_payslip_date_1(self):
        """
        Case 2: Test ngày kế toán trên phiếu lương, không có bảng lương
            Input: Tạo phiếu lương thủ công
            Output: Ngày kế toán của phiếu lương là False
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        self.assertFalse(payslip.date, 'Test date field not oke')

    def test_payslip_date_2(self):
        """
        Case 3: Test ngày kế toán trên phiếu lương, có bảng lương
            TH1: Bảng lương có ngày kế toán, có ngày kết thúc
                Output: Ngày kế toán của phiếu lương là ngày kế toán của bảng lương
        """
        batch = self.env['hr.payslip.run'].create({
            'name': 'Payslip Batch',
            'date_start': fields.Date.from_string('2021-7-1'),
            'date_end': fields.Date.from_string('2021-7-30'),
            'date': fields.Date.from_string('2021-8-1'),
            })
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.write({
            'payslip_run_id': batch.id
            })
        self.assertEqual(payslip.date, batch.date, 'Test date field not oke')

    def test_payslip_date_3(self):
        """
        Case 3: Test ngày kế toán trên phiếu lương, có bảng lương
            TH2: Bảng lương không có ngày kế toán, có ngày kết thúc
                Output: Ngày kế toán của phiếu lương là ngày kết thúc của bảng lương
        """
        batch = self.env['hr.payslip.run'].create({
            'name': 'Payslip Batch',
            'date_start': fields.Date.from_string('2021-7-1'),
            'date_end': fields.Date.from_string('2021-7-30'),
            })
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.write({
            'payslip_run_id': batch.id
            })
        self.assertEqual(payslip.date, batch.date_end, 'Test date field not oke')

    def test_payslip_confirm_1(self):
        """
        Case 4: Test điều kiện có thể xác nhận phiếu lương
            TH2: Phiếu lương có bảng lương, công ty có thiết lập gộp bút toán lương
                Output: Xác nhận không thành công thành công phiếu lương
        """
        self.env.company.write({
            'payslip_batch_journal_entry': True
        })
        batch = self.create_payslip_run()
        self.generate_payslip_run(batch, self.product_emp_A)

        with self.assertRaises(UserError):
            batch.slip_ids.action_payslip_verify()

    def test_payslip_confirm_2(self):
        """
        Case 4: Test điều kiện có thể xác nhận phiếu lương
            TH3: Phiếu lương có bảng lương, Công ty: không thiết lập gộp bút toán lương
                Output: Xác nhận thành công phiếu lương
        """
        self.env.company.write({
            'payslip_batch_journal_entry': False
        })
        batch = self.create_payslip_run()
        self.generate_payslip_run(batch, self.product_emp_A)
        batch.slip_ids.action_payslip_verify()
        
        self.assertEqual(batch.slip_ids.state, 'verify', 'Test Confirm Payslip not oke')
    
    def test_payslip_confirm_3(self):
        """
        Case 5: Test thông tin kế toán sau khi xác nhận phiếu lương
            TH1: Các quy tắc lương của cấu trúc lương không đánh dấu "Tạo phát sinh kế toán"
                Output: 
                    Không tạo ra bút toán liên quan đến phiếu lương này
                    Trường "Ngày kế toán" của phiếu lương để trống
        """
        rules = self.env['hr.salary.rule'].search([('company_id', '=', self.env.company.id)])
        rules.write({
            'generate_account_move_line': False
        })
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )

        moves_old = self.env['account.move'].search([('company_id', '=', self.env.company.id)])
        payslip.action_payslip_verify()
        moves_new = self.env['account.move'].search([('company_id', '=', self.env.company.id)])

        self.assertFalse(payslip.move_id, 'Test Accounting Entry not oke')
        self.assertFalse(payslip.date, 'Test Date Account not oke')
        self.assertEqual(moves_old, moves_new, 'Test auto create Journal Entries not oke')

    def test_payslip_confirm_4(self):
        """
        Case 5: Test thông tin kế toán sau khi xác nhận phiếu lương
            TH2: Các quy tắc lương của cấu trúc lương có đánh dấu "Tạo phát sinh kế toán"
                Có thiết lập tài khoản Nợ-có trên quy tắc lương (hoặc hợp đồng / phòng ban)
                Phiếu lương chưa chọn ngày kế toán
            Output:
                Tạo ra bút toán liên quan đến phiếu lương này
                Trường "Ngày kế toán" của phiếu lương là ngày kết thúc của phiếu lương
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        self.assertTrue(payslip.move_id, 'Test Accounting Entry not oke')
        self.assertEqual(payslip.date, fields.Date.from_string('2021-7-30'), 'Test Date Account not oke')

    def test_payslip_confirm_5(self):
        """
        Case 5: Test thông tin kế toán sau khi xác nhận phiếu lương
            TH3: Các quy tắc lương của cấu trúc lương có đánh dấu "Tạo phát sinh kế toán"
                Có thiết lập tài khoản Nợ-có trên quy tắc lương (hoặc hợp đồng / phòng ban)
                Phiếu lương đã chọn ngày kế toán
            Output:
                Tạo ra bút toán liên quan đến phiếu lương này
                Trường "Ngày kế toán" của phiếu lương không thay đổi
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.write({'date': fields.Date.from_string('2021-8-5')})
        payslip.action_payslip_verify()

        self.assertTrue(payslip.move_id, 'Test Accounting Entry not oke')
        self.assertEqual(payslip.date, fields.Date.from_string('2021-8-5'), 'Test Date Account not oke')

    def test_payslip_confirm_6(self):
        """
        Case 5: Test thông tin kế toán sau khi xác nhận phiếu lương
            TH4: Các quy tắc lương của cấu trúc lương có đánh dấu "Tạo phát sinh kế toán"
                Không thiết lập tài khoản Nợ-có trên quy tắc lương (hoặc hợp đồng / phòng ban)
                Phiếu lương đã chọn ngày kế toán
            Output:
                Không tạo ra bút toán liên quan đến phiếu lương này
                Trường "Ngày kế toán" của phiếu lương không thay đổi
        """
        self.env['hr.salary.rule'].search([
            ('company_id', '=', self.env.company.id)
            ])\
            .write({
                'generate_account_move_line': True,
                'account_debit': False,
                'account_credit': False,
                })
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        self.assertFalse(payslip.move_id, 'Test Accounting Entry not oke')
        self.assertFalse(payslip.date, 'Test Date Account not oke')

    def test_payslip_cancel(self):
        """
        Case 6: Test Hủy phiếu lương đã có bút toán chưa được đối soát
            Input: Phiếu lương đã có bút toán, bút toán chưa đối soát, ấn hủy phiếu lương
            Output: Hủy thành công phiếu lương, trạng thái phiếu lương là đã hủy
                    bút toán bị xóa
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()
        account_entry = payslip.move_id
        payslip.action_payslip_cancel()

        self.assertEqual(payslip.state, 'cancel', 'Test cancel payslip with account entry not oke')
        self.assertFalse(payslip.move_id, 'Test cancel payslip with account entry not oke')
        self.assertFalse(account_entry.exists(), 'Test cancel payslip with account entry not oke')

    def test_payslip_cancel_that_have_been_link_to_reconciled_entries(self):
        """
        Case 7: Test Hủy phiếu lương đã có bút toán đã đối soát, hoặc đối soát 1 phần

        Input: Phiếu lương đã có bút toán, bút toán đã đối soát hoặc đối soát 1 phần, ấn hủy phiếu lương
            TH1: Người dùng có quyền nhóm "kế toán viên" và Quản lý tại Bảng lương
            TH2: Người dùng không có quyền nhóm "kế toán viên" và có quyền Quản lý tại Bảng lương
        Output:
            TH1: Hủy thành công phiếu lương, bút toán bị xóa
            TH2: Hủy không thành công, thông báo ngoại lệ
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        bank_journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('currency_id', '=', False),
            ('type', '=', 'bank')
            ], limit = 1)
        # Create a bank statement
        bank_stmt = self.env['account.bank.statement'].create({
            'journal_id': bank_journal.id,
            'date': '2021-08-01',
            'line_ids': [
                (0, 0, {
                    'name': 'salary payment',
                    'amount': -payslip.move_id.amount_total,
                    'date': '2021-08-01',
                })
            ],
        })
        # Reconcile the bank statement with the invoice.
        credit_lines = payslip.move_id.line_ids.filtered(lambda line: not payslip.move_id.currency_id.is_zero(line.credit))
        bank_stmt.line_ids[0].process_reconciliation(counterpart_aml_dicts=[{
            'name': line.name,
            'debit': line.credit,
            'credit': 0,
            'move_line': line,
            } for line in credit_lines])

        # Ensure that reconciled
        self.assertTrue(payslip.move_id.line_ids.full_reconcile_id)

        # Input: TH2: người dùng không có quyền nhóm "kế toán viên" và có quyền Quản lý tại Bảng lương
        # Output: TH2: Hủy không thành công, thông báo ngoại lệ
        self.env.user.write({'groups_id': [(6, 0, [
            self.ref('to_hr_payroll.group_hr_payroll_manager'),
            self.ref('account.group_account_invoice'),
            ])]})
        with self.assertRaises(UserError):
            payslip.action_payslip_cancel()

        # Input: TH1: Người dùng có quyền nhóm "kế toán viên" và Quản lý tại Bảng lương
        # Output: TH1: Hủy thành công phiếu lương, bút toán bị xóa
        self.env.user.write({'groups_id': [(6, 0, [
            self.ref('to_hr_payroll.group_hr_payroll_manager'),
            self.ref('account.group_account_user'),
            ])]})
        payslip.action_payslip_cancel()

    def test_payslip_refund(self):
        """
       Case 8: Test Hoàn trả phiếu lương - Kiểm tra bút toán phát sinh
            Input: Hoàn trả Phiếu lương đã có bút toán
            Output: Xác nhận thành công. 
                Sinh ra bút toán được ghi vào sổ nhật ký lương với các định khoản Nợ - Có ngược lại với định khoản ban đầu
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()
        payslip.refund_sheet()

        account_entry_refund = payslip.refund_ids.move_id
        self.assertTrue(account_entry_refund, 'Test Refund Payslip not oke')
        self.assertRecordValues(
            payslip.move_id.line_ids,
            [
                {
                    'account_id': line.account_id.id,
                    'debit': line.credit,
                    'credit': line.debit,
                    }
                for line in account_entry_refund.line_ids
                ]
            )
