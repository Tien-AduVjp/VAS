from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        analytic_tags = self.product_id.sudo().asset_category_id.analytic_tag_ids
        if analytic_tags:
            analytic_tag_ids = analytic_tags.ids + res['analytic_tag_ids'][0][2]
            res['analytic_tag_ids'][0] = (6, 0, analytic_tag_ids)
        return res
