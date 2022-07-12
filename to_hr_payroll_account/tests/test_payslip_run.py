from odoo.tests.common import Form, tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestPayslipRun(TestCommon):

    def test_form_payslip_run(self):
        """
        Case 1: Test Trường sổ nhật ký mặc định là sổ "Lương nhân viên" mã "SAL" khi tạo bảng lương
            Input: Mở form bảng lương mới
            Output: Sổ nhật ký mặc định là "Lương nhân viên", mã "SAL"
        """
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'SAL')
            ], limit = 1)
        f = Form(self.env['hr.payslip.run'])
        self.assertEqual(f.journal_id, journal, 'Test default field: journal_id not oke')

    def test_payslip_batch_confirm_1(self):
        """
        Case 1: Xác nhận bảng lương
            Input:
                Công ty không đánh dấu "Bút toán cho Bảng lương"
                Bảng lương với nhiều phiếu lương
                Có các tài khoản nợ có trên quy tắc lương (hợp đồng  / phòng ban)
                Xác nhận bảng lương
            Ouput:
                Sinh ra các bút toán riêng biệt của từng phiếu lương trong bảng lương
        """
        employees = self.product_emp_A + self.product_dep_manager
        batch = self.create_payslip_run()
        self.generate_payslip_run(batch, employees)
        batch.action_verify_payslips()

        payslip_1 = batch.slip_ids[0]
        payslip_2 = batch.slip_ids[1]
        self.assertTrue(payslip_1.move_id, 'Test Journal Entries on payslips not oke')
        self.assertTrue(payslip_2.move_id, 'Test Journal Entries on payslips not oke')
        self.assertNotEqual(payslip_1.move_id, payslip_2.move_id, 'Test Journal Entries on payslips not oke')

    def test_payslip_batch_confirm_2(self):
        """
        Case 2: Xác nhận bảng lương
            Input:
                Công ty có đánh dấu "Bút toán cho Bảng lương"
                Bảng lương với nhiều phiếu lương
                Có các tài khoản nợ có trên quy tắc lương (hợp đồng  / phòng ban)
                Xác nhận bảng lương
            Ouput:
                Sinh ra 1 bút toán cho bảng lương, thông tin bút toán bao gồm của 2 các phiếu lương
        """
        self.env.company.write({
            'payslip_batch_journal_entry': True
            })

        employees = self.product_emp_A + self.product_dep_manager
        batch = self.create_payslip_run()
        self.generate_payslip_run(batch, employees)
        batch.action_verify_payslips()

        payslip_1 = batch.slip_ids[0]
        payslip_2 = batch.slip_ids[1]
        self.assertTrue(payslip_1.move_id, 'Test Journal Entries on payslips not oke')
        self.assertTrue(payslip_2.move_id, 'Test Journal Entries on payslips not oke')
        self.assertEqual(payslip_1.move_id, payslip_2.move_id, 'Test Journal Entries on payslips not oke')

    def test_payslip_batch_cancel_1(self):
        """
        Case 4: Hủy bảng lương
            TH2: Công ty có đánh dấu Bút toán toán cho bảng lương
                 Hủy bảng lương có bút toán chưa được đối soát
            Output:
                Hủy thành công Bảng lương, bút toán sinh ra bị xóa
        """
        batch = self.create_payslip_run()
        self.generate_payslip_run(batch, self.product_emp_A)
        batch.action_verify_payslips()
        batch.action_cancel()

        self.assertEqual(batch.state, 'cancelled', 'Test cancel Payslips Batche not oke')
        self.assertFalse(batch.slip_ids.move_id, 'Test cancel Payslips Batche not oke')
