from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense Report")

    def post(self):
        res = super(AccountPayment, self).post()
        for r in self:
            if r.expense_sheet_id:
                vendors = r.expense_sheet_id.expense_line_ids.vendor_id
                if len(vendors) == 1:
                    r.write({'partner_id': vendors.id})
        return res
