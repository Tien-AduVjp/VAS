from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    expense_payment_mode = fields.Selection(related='expense_sheet_id.payment_mode', string='Expense Payment Mode')
