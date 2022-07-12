from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_inter_comp_sale_order_line_data(self, sale_order):
        """
        Generate the Sales Order Line values from the PO line
        """
        vals = super(PurchaseOrderLine, self)._prepare_inter_comp_sale_order_line_data(sale_order)
        vals.update({
            'customer_lead': self.product_id and self.product_id.sale_delay or 0.0,
            })
        return vals

