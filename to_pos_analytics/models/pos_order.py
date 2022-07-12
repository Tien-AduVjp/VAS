from odoo import models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder, self)._prepare_invoice_line(order_line)
        if order_line.order_id.config_id.analytics_account_id:
            res['analytic_account_id'] = order_line.order_id.config_id.analytics_account_id.id
        return res
