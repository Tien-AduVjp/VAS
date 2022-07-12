from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tests.common import Form


@tagged('post_install', '-at_install')
class TestHrContract(TransactionCase):

    def test_form_contract_1(self):
        """
        Case 1: Test Trường sổ nhật ký mặc định là sổ "Lương nhân viên" mã "SAL" khi tạo hợp đồng
            Input: Mở form hợp đồng mới - người dùng không nằm trong nhóm kế toán viên
            Output: không hiển thị sổ nhật ký trên form hợp đồng
        """
        f = Form(self.env['hr.contract'])
        with self.assertRaises(AssertionError):
            f.journal_id = False

    def test_form_contract_2(self):
        """
        Case 1: Test Trường sổ nhật ký mặc định là sổ "Lương nhân viên" mã "SAL" khi tạo hợp đồng
            Input: Mở form hợp đồng mới - người dùng nằm trong nhóm kế toán viên
            Output: Sổ nhật ký mặc định là "Lương nhân viên", mã "SAL"
        """
        self.env.user.write({
            'groups_id': [(4,self.env.ref("account.group_account_user").id,0)]
            })
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'SAL')
            ], limit = 1)
        f = Form(self.env['hr.contract'])
        self.assertEqual(f.journal_id, journal, 'Test default field: journal_id not oke')
