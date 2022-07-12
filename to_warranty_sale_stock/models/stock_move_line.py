from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_warranty_policy_ids(self):
        res = super(StockMoveLine, self)._get_warranty_policy_ids()
        if self.move_id.sale_line_id:
            warranty_policy_ids = self.move_id.sale_line_id.sudo().mapped('warranty_policy_ids')
            res = warranty_policy_ids
        return res
