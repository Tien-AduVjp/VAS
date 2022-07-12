from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.sheet.register.payment.wizard"
    
    @api.model
    def _default_employee_id(self):
        active_id = self._context.get('active_id', [])
        expense_sheet = self.expense_sheet_id or self.env['hr.expense.sheet'].browse(active_id)
        return expense_sheet.employee_id.id
    
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee_id)
    is_advance_journal = fields.Boolean(related='journal_id.is_advance_journal')
    
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if not self.journal_id.is_advance_journal:
            self.employee_id = False
        elif not self.employee_id:
            self.employee_id = self._default_employee_id()
    
    def _get_payment_vals(self):
        res = super(HrExpenseSheetRegisterPaymentWizard, self)._get_payment_vals()
        if self.journal_id.is_advance_journal:
            if self.employee_id.sudo().address_home_id:
                res['employee_id'] = self.employee_id.id
            else:
                raise ValidationError(_("The employee '%s' you've selected has no Private Address specified. Please specify one for this employee first.")
                                  % (self.employee_id.name,))
        return res
