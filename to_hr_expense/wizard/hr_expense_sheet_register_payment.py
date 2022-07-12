from odoo import api, models


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.sheet.register.payment.wizard"

#     @api.model
#     def default_get(self, fields):
#         res = super(HrExpenseSheetRegisterPaymentWizard, self).default_get(fields)
#         if 'expense_sheet_id' in res:
#             expense_sheet = self.env['hr.expense.sheet'].browse([res['expense_sheet_id']])
#             
#             vendor = expense_sheet.expense_line_ids.mapped('vendor_id')
#             if len(vendor) == 1:
#                     res['partner_id'] = vendor.id
#         return res
    
    def _get_payment_vals(self):
        res = super(HrExpenseSheetRegisterPaymentWizard, self)._get_payment_vals()
        res['expense_sheet_id'] = self.expense_sheet_id.id
        return res