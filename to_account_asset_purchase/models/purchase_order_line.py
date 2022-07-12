from odoo import  models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        data = super(PurchaseOrderLine, self)._prepare_account_move_line(move=move)
        if self.product_id.asset_category_id:
            data['asset_category_id'] = self.product_id.asset_category_id.id
        return data
