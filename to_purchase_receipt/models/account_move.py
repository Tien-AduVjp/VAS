from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if any(arg in vals for arg in ['move_type', 'state']):
            self.invoice_line_ids.purchase_order_id._check_invoice_ids()
        return res
