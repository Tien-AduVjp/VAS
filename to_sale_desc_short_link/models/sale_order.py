from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_shorten_urls_in_name(self):
        """
        Button shorten urls in action
        :return: updated content with url in sale.order.line and sale.order.option
        """
        self.mapped('order_line').shorten_urls_in_name()
        self.mapped('sale_order_option_ids').shorten_urls_in_name()

    def _shorten_urls_text(self, content):
        """
        Shorten urls in a string content
        :return: updated content
        """
        self.ensure_one()
        order_tracker_vals = {
            'source_id' : self.source_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
        }
        return self.env['mail.render.mixin'].sudo()._shorten_links_text(content, order_tracker_vals)
