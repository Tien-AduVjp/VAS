from datetime import date, timedelta

from odoo.tests import Form, tagged, SavepointCase
from odoo.exceptions import MissingError, ValidationError


@tagged('-at_install', 'post_install')
class TestExpensePayroll(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestExpensePayroll, cls).setUpClass()
        
        cls.employee = cls.env.ref('hr.employee_al')
        
        contract = cls.env.ref('hr_contract.hr_contract_al')
        contract.date_start = date(2021, 1, 1)
        
        cls.expense = cls.env['hr.expense'].create({
                'name': 'expense travel',
                'vendor_id': cls.env.ref('base.res_partner_1').id,
                'employee_id': cls.employee.id,
                'product_id': cls.env.ref('hr_expense.car_travel').id,
                'unit_amount': 999,
                'payment_mode': 'own_account',
                'reimbursed_in_payslip': True,
                'date': date(2021, 5, 5)
            })
        
        cls.expense.action_submit_expenses()
        cls.expense_sheet = cls.expense.sheet_id
        
        cls.expense_2 = cls.env['hr.expense'].create({
            'name': 'expense travel',
            'vendor_id': cls.env.ref('base.res_partner_1').id,
            'employee_id': cls.employee.id,
            'product_id': cls.env.ref('hr_expense.car_travel').id,
            'unit_amount': 1999,
            'payment_mode': 'own_account',
            'reimbursed_in_payslip': True,
            'date': date(2021, 5, 6)
        })
        
    def approve_expense_sheet(self, expense_sheet):
        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        
    def create_payslip(self, emp, start_period, end_period=False):
        payslip = self.env['hr.payslip'].create({
                'employee_id': emp.id,
                'date_from': start_period,
                'date_to': end_period or start_period + timedelta(days=31),
                'company_id': self.env.company.id,
                'contract_id': self.employee.contract_id.id
            })
        return payslip

    def done_payslip(self, payslip):
        payslip.action_payslip_verify()
        payslip.action_payslip_done()

    def test_onchange_payment_mode(self):
        expense_form = Form(self.expense)
        expense_form.payment_mode = 'company_account'
        self.assertTrue(expense_form._get_modifier('reimbursed_in_payslip', 'invisible'))
        expense = expense_form.save()
        self.assertFalse(expense.reimbursed_in_payslip)

    def test_payslip_expense_linking(self):
        """
        Case 1.1: Test thông tin Chi tiêu khi nhấn nút tính toán lương / xác nhận phiếu lương
        Input: Phiếu lương nhân viên, Chi tiêu của nhân viên với các TH sau:
        TH1: Chi tiêu ở trạng thái đã duyệt, Thanh toán bởi nhân viên, có đánh dấu bồi hoàn nhân viên, chưa liên quan đến phiếu lương nào
        TH2:  Chi tiêu ở trạng thái đã duyệt, Thanh toán bởi nhân viên, có đánh dấu bồi hoàn nhân viên, liên quan đến phiếu lương đang thực hiện tính toán lương
        Th3: các tiêu chí không nằm trong TH1,TH2
        Output:
        TH1, 2: Các chi tiêu hợp lệ được gán đến phiếu lương tương ứng, số tiền bồi hoàn được thể hiện ở dòng phiếu lương NET
        TH3: Không cập nhật chi tiêu liên quan đến phiếu lương, Phiếu lương không bị ảnh hưởng bởi chi tiêu, nếu có
        """
        payslip = self.create_payslip(self.employee, date(2021, 4, 1))
        self.approve_expense_sheet(self.expense_sheet)
        payslip.compute_sheet()
        self.assertNotIn(self.expense, payslip.hr_expense_ids)
        payslip.date_to = date(2021, 6, 1)
        payslip.compute_sheet()
        self.assertIn(self.expense, payslip.hr_expense_ids)
        payslip_expense_line = payslip.line_ids.filtered(lambda r: r.code == 'EXREIMB')
        self.assertEqual(payslip_expense_line.total, 999)
        # Check case recompute
        payslip.compute_sheet()
        self.assertIn(self.expense, payslip.hr_expense_ids)  
        # Check case copy hr_expense
        self.assertNotEqual(self.expense.copy().hr_payslip_id, payslip)

        # Case not linking
        payslip2 = self.create_payslip(self.employee, date(2021, 5, 1))
        payslip2.compute_sheet()
        self.assertNotIn(self.expense, payslip2.hr_expense_ids)
        with self.assertRaises(MissingError), self.cr.savepoint():
            self.expense_2.reimbursed_in_payslip = False
            self.expense_2.action_submit_expenses()
            new_payslip = self.create_payslip(self.employee, date(2021, 5, 1))
            self.assertNotIn(self.expense_2, new_payslip.hr_expense_ids)
            raise MissingError('trick to rollback')
        """
        Case 3.1: Test xem phiếu lương trên bảng kê chi tiêu
        Input: nhấn xem phiếu lương trên bảng kê chi tiêu
        Output: 
        TH1: Có 1 phiếu lương, chế độ xem kiểu form
        TH2: Có nhiều hơn 1 phiếu lương, danh sách phiếu lương tương ứng
        """
        action_view_payslip = self.expense_sheet.action_view_payslips()
        self.assertEqual(action_view_payslip.get('res_id'), payslip.id)

        self.expense_sheet.expense_line_ids = [(4, self.expense_2.id)]
        payslip2 = self.create_payslip(self.employee, date(2021, 5, 1))
        payslip2.compute_sheet()
        action_view_payslip = self.expense_sheet.action_view_payslips()
        self.assertEqual(action_view_payslip.get('res_id'), False)

        """
        Case 1.2: Test nút Hoàn thành phiếu lương, có chi tiêu liên quan đến phiếu lương này
        Input: Phiếu lương, nhấn hoàn thành phiếu lương
        Ouput: Các thông tin của chi tiêu được cập nhật
                Tất cả chi tiêu liên quan đến phiếu lương có trạng thái là đã thanh toán
                Bảng kê chi tiêu tương ứng với các chi tiêu có trạng thái là đã thanh toán
        Case 1.3: test nút hủy phiếu lương, có chi tiêu liên quan đến phiếu lương này
        Input: Phiếu lương, nhấn hủy phiếu lương
        Output: Hủy liên kết giữa phiếu lương và chi tiêu
        """
        with self.assertRaises(MissingError), self.cr.savepoint():
            self.done_payslip(payslip)
            self.assertEqual(self.expense.state, 'done')
            self.assertNotEqual(self.expense_2.state, 'done')
            self.assertNotEqual(self.expense_sheet.state, 'done')
            self.done_payslip(payslip2)
            self.assertEqual(self.expense.state, 'done')
            self.assertEqual(self.expense_2.state, 'done')
            self.assertEqual(self.expense_sheet.state, 'done')
            raise MissingError('trick to rollback')
        
        # Case post journal for expense_sheet first
        self.expense_sheet.action_sheet_move_create()
        self.done_payslip(payslip)
        self.done_payslip(payslip2)
        self.assertEqual(self.expense.state, 'done')
        self.assertEqual(self.expense_sheet.state, 'done')
        
        payslip.action_payslip_cancel()
        self.assertNotIn(self.expense, payslip.hr_expense_ids)
        self.assertEqual(self.expense.state, 'approved')
        self.assertEqual(self.expense_sheet.state, 'post'),
        
        # Recompute after cancel
        payslip.action_payslip_draft()
        payslip.compute_sheet()
        self.assertIn(self.expense, payslip.hr_expense_ids)

    def test_expense_constraint(self):
        """
        Case 2.1 Test Ràng buộc: "Bồi hoàn chi tiêu" và ngoại tệ
        """
        self.assertRaises(ValidationError, self.expense.write, {'currency_id': self.env.ref('base.VND')})
        with self.assertRaises(ValidationError):
            self.env['hr.expense'].create({
                'name': 'expense travel',
                'vendor_id': self.env.ref('base.res_partner_1').id,
                'employee_id': self.employee.id,
                'product_id': self.env.ref('hr_expense.car_travel').id,
                'payment_mode': 'own_account',
                'reimbursed_in_payslip': True,
                'currency_id': self.env.ref('base.VND').id,
                'unit_amount': 999
            })

    def test_compute_is_paid_1(self):
        self.approve_expense_sheet(self.expense_sheet)
        self.assertTrue(self.expense_sheet.is_paid)
        
    def test_compute_is_paid_2(self):
        self.expense.reimbursed_in_payslip = False
        self.approve_expense_sheet(self.expense_sheet)
        self.assertFalse(self.expense_sheet.is_paid)

    def test_sheet_mix_type_expense(self):
        # Case có các dòng chi phí khác kiểu (bồi hoàn phiếu lương và không)
        self.expense_2.reimbursed_in_payslip = False
        self.expense_sheet.expense_line_ids = [(4, self.expense_2.id)]
        self.approve_expense_sheet(self.expense_sheet)
        self.expense_sheet.action_sheet_move_create()
        
        # Pay expense1 by create payslip
        payslip = self.create_payslip(self.employee, date(2021, 6, 1))
        payslip.compute_sheet()
        self.done_payslip(payslip)
        self.assertNotEqual(self.expense_sheet.state, 'done')

        # Pay expense2 by create payment
        journal_bank = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        form_payment = Form(self.env['hr.expense.sheet.register.payment.wizard'].with_context(default_payment_type='inbound', 
                                                                               active_id=self.expense_sheet.id,
                                                                               active_ids=self.expense_sheet.ids,
                                                                               active_model='hr.expense.sheet'))
        self.assertEqual(form_payment.amount, 1999)
        form_payment.amount = 200
        form_payment.journal_id = journal_bank
        form_payment.save().expense_post_payment()
        
        self.assertFalse(self.expense_sheet.is_paid)
        form_payment = Form(self.env['hr.expense.sheet.register.payment.wizard'].with_context(default_payment_type='inbound', 
                                                                               active_id=self.expense_sheet.id,
                                                                               active_ids=self.expense_sheet.ids,
                                                                               active_model='hr.expense.sheet'))
        self.assertEqual(form_payment.amount, 1799)
        form_payment.journal_id = journal_bank
        form_payment.save().expense_post_payment()
        self.assertTrue(self.expense_sheet.is_paid)
        self.assertEqual(self.expense_sheet.state, 'done')

        # Cancel payslip and recheck
        payslip.action_payslip_cancel()
        self.assertNotEqual(self.expense_sheet.state, 'done')
