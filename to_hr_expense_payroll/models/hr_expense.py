from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    reimbursed_in_payslip = fields.Boolean(string='Reimbursed in Payslip', default=False,
                                           readonly=False, states={'reported': [('readonly', True)],
                                                                   'approved': [('readonly', True)],
                                                                   'done': [('readonly', True)]},
                                           help="If checked, this expense will be included in the next HR Payslip."
                                           " No direct payment on the expense anymore.")
    hr_payslip_id = fields.Many2one('hr.payslip', string='Payslip', readonly=True, copy=False)

    @api.constrains('reimbursed_in_payslip', 'currency_id', 'company_id')
    def _check_expense_payroll_currency(self):
        for r in self:
            if r.currency_id != r.company_id.currency_id and r.reimbursed_in_payslip:
                raise ValidationError(_("Could not set Reimbursed in Payslip for the expense '%s [%s]' while its currency differs from the"
                                        " corresponding company's currency. You may need to uncheck the Reimbursed in Payslip first.")
                                        % (r.name, r.employee_id.name))

    @api.onchange('payment_mode')
    def _onchange_payment_mode(self):
        if self.payment_mode != 'own_account':
            self.reimbursed_in_payslip = False
