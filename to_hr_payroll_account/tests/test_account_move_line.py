from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestAccountMove(TestCommon):

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
