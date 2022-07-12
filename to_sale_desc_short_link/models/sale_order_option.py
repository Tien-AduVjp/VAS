from odoo import models, api

class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    def write(self, vals):
        shorten_urls = 'name' in vals and not self._context.get('do_not_shorten_urls_during_write')
        if shorten_urls and self and self.order_id:
            vals['name'] = self.order_id[0]._shorten_urls_text(vals['name'])
        return super(SaleOrderOption, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '') and vals.get('order_id', False):
                order = self.env['sale.order'].browse(vals['order_id']).sudo()
                vals['name'] = order._shorten_urls_text(vals['name'])
        return super(SaleOrderOption, self).create(vals_list)

    def shorten_urls_in_name(self):
        for r in self:
            r.name = r.order_id._shorten_urls_text(r.name)
