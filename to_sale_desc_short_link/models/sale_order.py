from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_shorten_urls_in_name(self):
        self.mapped('order_line').shorten_urls_in_name()
