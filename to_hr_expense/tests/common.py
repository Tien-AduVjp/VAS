import logging

from odoo.tests import SavepointCase, Form

_logger = logging.getLogger(__name__)


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        chart_template = cls.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            _logger.warning("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")

        cls.partner = cls.env.ref('base.res_partner_1')

        cls.expense_sheet = cls.env.ref('hr_expense.office_furniture_sheet')
        cls.expense_employee = cls.env.ref('hr.employee_al')
        cls.product_a = cls.env.ref('product.product_delivery_01')
        cls.expense_sheet.expense_line_ids.write({
            'to_invoice': True,
            'vendor_id': cls.partner.id,
            'currency_id': cls.env.company.currency_id.id
            })

        vendor_journals = cls.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', cls.env.company.id)])
        vendor_journal = vendor_journals[0]
        expense_journal = vendor_journals.filtered(lambda j: j.code == 'EXJ')[0]
        cls.default_journal_bank = cls.env.company.bank_journal_ids[:1]
        cls.expense_sheet.write({
            'bank_journal_id': cls.default_journal_bank.id,
            'journal_id': expense_journal.id,
            'vendor_bill_journal_id': vendor_journal.id,
            'currency_id': cls.env.company.currency_id.id,
            'payment_mode': 'own_account',
            })

    def post_hr_expense_sheet(self, expense_sheet):
        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()
        return expense_sheet

    def register_payment_hr_expense_sheet_employee_paid(self, expense_sheet):
        posted_expense_sheet = self.post_hr_expense_sheet(expense_sheet)
        action_data = posted_expense_sheet.action_register_payment()
        context = action_data['context']
        context.update({
            'active_model': 'account.move',
            'expense_ids': posted_expense_sheet.ids,
            'active_ids': posted_expense_sheet.move_ids.ids,
        })
        wizard =  Form(self.env['account.payment.register'].with_context(context)).save()
        account_payments = wizard._create_payments()
        return account_payments

    def cancel_hr_expense_sheet_posted(self, expense_sheet):
        self.env['hr.expense.refuse.wizard'].with_context(hr_expense_refuse_model='hr.expense.sheet',
                                                          active_ids=[expense_sheet.id],
                                                          active_id=expense_sheet.id) \
                                            .create({'reason': 'Mistake'}).expense_refuse_reason()

    def _check_account_move_line(self, move_lines, debit_code, debit_partner, debit_amount, credit_code, credit_partner, credit_amount):
        """
        Check the accounts, amounts in the journal items
        """
        debit_line = move_lines.filtered(lambda m: m.debit > 0)
        credit_line = move_lines.filtered(lambda m: m.credit > 0)
        self.assertEqual(debit_line.partner_id.id, debit_partner.id, "Wrong debit partner")
        self.assertEqual(credit_line.partner_id.id, credit_partner.id, "Wrong credit partner")
        self.assertEqual(debit_line.account_id.code, debit_code, "Wrong debit account")
        self.assertEqual(credit_line.account_id.code, credit_code, "Wrong credit account")
        self.assertEqual(sum(debit_line.mapped('debit')), debit_amount, "Wrong debit amount")
        self.assertEqual(sum(credit_line.mapped('credit')), credit_amount, "Wrong credit amount")

    def get_payment(self, expense_sheet, amount):
        ctx = {
            'active_model': 'account.move',
            'active_ids': expense_sheet.move_ids.filtered_domain([
                ('move_type', '=', 'entry'),
                ('state', '=', 'posted')
                ]).ids
        }
        payment_register = self.env['account.payment.register'].with_context(**ctx).create({
            'amount': amount,
            'journal_id': self.default_journal_bank.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
        })
        return payment_register._create_payments()
