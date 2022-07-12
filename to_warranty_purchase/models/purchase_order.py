from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for line in self.mapped('order_line'):
            line.warranty_policy_ids = line.mapped('product_id.warranty_policy_ids').filtered(lambda x: x.apply_to == 'purchase')
        return super(PurchaseOrder, self).button_confirm()
