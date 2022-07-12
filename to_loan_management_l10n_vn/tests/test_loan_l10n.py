from datetime import date

from odoo.addons.to_loan_management.tests.common import TestLoanCommon
from odoo.tests import tagged, Form


@tagged('post_install', '-at_install')
class TestLoanL10nVn(TestLoanCommon):

    @classmethod
    def setUpClass(cls, company=None):
        super().setUpClass(company=company)
        chart_template_vn = cls.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        company = cls.env['res.company'].create({'name': 'khaihoan'})
        chart_template_vn.try_loading(company=company)
        cls.env.company = company
        cls.company = company
        cls.env.user.groups_id += cls.env.ref('analytic.group_analytic_accounting')
        cls.account_3411 = cls.env['account.account'].search(
            [('company_id', '=', cls.company.id), ('code', 'like', '3411' + '%')], limit=1)
        cls.account_1283 = cls.env['account.account'].search(
            [('company_id', '=', cls.company.id), ('code', 'like', '1283' + '%')], limit=1)
        cls.account_515 = cls.env['account.account'].search(
            [('company_id', '=', cls.company.id), ('code', 'like', '515' + '%')], limit=1)
        cls.account_635 = cls.env['account.account'].search(
            [('company_id', '=', cls.company.id), ('code', 'like', '635' + '%')], limit=1)
        cls.journal_loan_borrow = cls.env['account.journal'].search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'purchase'),
            '|', ('code', '=', 'BLJ'), ('name', 'ilike', 'Borrowing Loans Journal')], limit=1)
        cls.journal_loan_lend = cls.env['account.journal'].search([
            ('company_id', '=', cls.company.id),
            ('type', '=', 'sale'),
            '|', ('code', '=', 'LLJ'), ('name', 'ilike', 'Lending Loans Journal')], limit=1)
        cls.lending_loan_tag = cls.env.ref('l10n_vn_c200.analytic_tag_interests_dividends_distributed_profits')
        cls.borrowing_loan_tag = cls.env.ref('l10n_vn_c200.analytic_tag_borrowing_loan')

    def create_loan_order(self, model, loan_amount, interest_rate_type):
        return self.env[model].create({
            'partner_id': self.partner.id,
            'loan_amount': loan_amount,
            'interest_rate_type_id': interest_rate_type.id,
            'expiry_interest_rate_type_id': interest_rate_type.id,
            'date_confirmed': date(2021, 10, 15),
        })

    def init_invoice(self, move_type):
        move_form = Form(self.env['account.move'].with_context(default_type=move_type))
        move_form.invoice_date = date(2021, 10, 15)
        move_form.partner_id = self.partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_loan
        return move_form.save()

    def test_check_setting(self):
        self.assertRecordValues(self.company, [
            {
                'loan_borrowing_journal_id': self.journal_loan_borrow.id,
                'loan_borrowing_account_id': self.account_3411.id,
                'loan_lending_journal_id': self.journal_loan_lend.id,
                'loan_lending_account_id': self.account_1283.id,
            }
        ])

    def test_check_journal_loan_borrow(self):
        self.assertRecordValues(self.journal_loan_borrow, [
            {
                'default_debit_account_id': self.account_3411.id,
                'default_credit_account_id': self.account_3411.id,
            }
        ])

    def test_check_journal_loan_lend(self):
        self.assertRecordValues(self.journal_loan_lend, [
            {
                'default_debit_account_id': self.account_1283.id,
                'default_credit_account_id': self.account_1283.id,
            }
        ])

    def test_check_product_category_loan(self):
        self.assertRecordValues(self.product_category_loan_interest, [
            {
                'property_account_income_categ_id': self.account_515.id,
                'property_account_expense_categ_id': self.account_635.id,
            }
        ])

    def test_auto_add_analytic_tag_invoice(self):
        invoice = self.init_invoice('out_invoice')
        self.assertEqual(invoice.invoice_line_ids.analytic_tag_ids, self.lending_loan_tag)

    def test_auto_add_analytic_tag_bill(self):
        invoice = self.init_invoice('in_invoice')
        self.assertEqual(invoice.invoice_line_ids.analytic_tag_ids, self.borrowing_loan_tag)

    def test_auto_add_analytic_tag_borrowing_loan(self):
        order = self.create_loan_order('loan.borrowing.order', 100000000, self.interest_flat_rate_type_month)
        self.assertEqual(order.analytic_tag_ids, self.borrowing_loan_tag)

    def test_auto_add_analytic_tag_lending_loan(self):
        order = self.create_loan_order('loan.lending.order', 100000000, self.interest_flat_rate_type_month)
        self.assertEqual(order.analytic_tag_ids, self.lending_loan_tag)
