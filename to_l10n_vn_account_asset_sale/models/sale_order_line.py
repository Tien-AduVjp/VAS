from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.product_id.asset_category_id:
            fixed_asset_analytic_tag_id = self.env.ref('l10n_vn_c200.analytic_tag_fixed_assets')
            if fixed_asset_analytic_tag_id.id not in res['analytic_tag_ids'][0][2]:
                analytic_tag_ids = [fixed_asset_analytic_tag_id.id] + res['analytic_tag_ids'][0][2]
                res['analytic_tag_ids'][0] = (6, 0, analytic_tag_ids)
        return res
