from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def write(self, vals):
        shorten_urls = 'name' in vals and not self._context.get('do_not_shorten_urls_during_write')
        res = super(SaleOrderLine, self).write(vals)
        if shorten_urls:
            self.shorten_urls_in_name()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', ''):
                order = self.env['sale.order'].browse(vals.get('order_id', 0)).sudo()
                utm_source = order.source_id or False
                utm_campaign = order.campaign_id or False
                utm_medium = order.medium_id or False
                vals['name'] = self.env['shorten.url.mixin'].shorten_urls_in_text(vals['name'], utm_source, utm_campaign, utm_medium, 60)
        return super(SaleOrderLine, self).create(vals_list)

    def shorten_urls_in_name(self):
        for r in self.with_context(do_not_shorten_urls_during_write=True):
            r.name = self.env['shorten.url.mixin'].shorten_urls_in_text(
                r.name,
                r.order_id.source_id or False,
                r.order_id.campaign_id or False,
                r.order_id.medium_id or False,
                60)
