from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def _prepare_invoice_line(self):
        self.ensure_one()
        vals = super(SaleOrderLine, self)._prepare_invoice_line()
        vals['wallet'] = self.product_id.wallet
        return vals
