from odoo import api, models


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.sheet.register.payment.wizard"

    @api.model
    def default_get(self, fields):
        res = super(HrExpenseSheetRegisterPaymentWizard, self).default_get(fields)
        active_id = self._context.get('active_id',False)
        expense_sheet = self.env['hr.expense.sheet'].browse(active_id)
        if expense_sheet:
            res['amount'] = expense_sheet._get_amount()
        return res

    def _prepare_lines_to_reconcile(self, lines):
        return super(HrExpenseSheetRegisterPaymentWizard, self)._prepare_lines_to_reconcile(lines)\
            .filtered(lambda l: l.expense_id.reimbursed_in_payslip == False)

    def expense_post_payment(self):
        self.ensure_one()
        res = super(HrExpenseSheetRegisterPaymentWizard, self).expense_post_payment()
        expense_sheet = self.expense_sheet_id
        amount = expense_sheet._get_amount()
        if self.currency_id.is_zero(amount):
            expense_sheet.expense_line_ids.filtered(lambda r:r.reimbursed_in_payslip==False).write({'state': 'done'})
            expense_sheet.write({'is_paid': True})
            if all(expense_line_id.state == 'done' for expense_line_id in expense_sheet.expense_line_ids):
                expense_sheet.set_to_paid()
        return res
