from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_warranty_policy_ids(self):
        res = super(StockMoveLine, self)._get_warranty_policy_ids()
        if self.move_id.purchase_line_id:
            warranty_policy_ids = self.move_id.purchase_line_id.mapped('warranty_policy_ids')
            res = warranty_policy_ids
        return res
