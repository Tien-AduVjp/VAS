from odoo import models, api, fields


class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def _default_expense_sheet_id(self):
        return self.env['hr.expense.sheet'].search([('id', 'in', self.env.context.get('expense_ids', 0))])

    expense_sheet_id = fields.Many2one('hr.expense.sheet', string='Expense Report', default=_default_expense_sheet_id)

    def _create_payment_vals_from_wizard(self):
        res = super(PaymentRegister, self)._create_payment_vals_from_wizard()
        if self.expense_sheet_id:
            res.update({
                'expense_sheet_id': self.expense_sheet_id.id,
            })
            if self.expense_sheet_id.payment_mode == 'own_account':
                res.update({
                    'destination_account_id': self.expense_sheet_id.employee_id.sudo().address_home_id.property_account_payable_id.id,
                    'partner_id': self.expense_sheet_id.employee_id.sudo().address_home_id.commercial_partner_id.id,
                })
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(PaymentRegister, self)._create_payment_vals_from_batch(batch_result)
        if self.expense_sheet_id:
            res.update({
                'expense_sheet_id': self.expense_sheet_id.id,
            })
            if self.expense_sheet_id.payment_mode == 'own_account':
                res.update({
                    'destination_account_id': self.expense_sheet_id.employee_id.sudo().address_home_id.property_account_payable_id.id,
                    'partner_id': self.expense_sheet_id.employee_id.sudo().address_home_id.commercial_partner_id.id,
                })
        return res

    def _init_payments(self, to_process, edit_mode=False):
        payments = super(PaymentRegister, self)._init_payments(to_process, edit_mode=edit_mode)
        payments.move_id.write({'hr_expense_sheet_id': self.expense_sheet_id.id})
        for line in payments.move_id.line_ids:
            if line.expense_id:
                if line.account_id.internal_type in ('receivable', 'payable'):
                    line.exclude_from_invoice_tab = True
                else:
                    line.exclude_from_invoice_tab = False
        return payments
