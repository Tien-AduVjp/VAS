from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for line in self.mapped('order_line'):
            line.warranty_policy_ids = line.mapped('product_id.warranty_policy_ids').filtered(lambda x: x.apply_to == 'sale')
        return super(SaleOrder, self).action_confirm()

