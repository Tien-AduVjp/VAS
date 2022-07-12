from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('is_promotion_voucher')
    def _onchange_is_promotion_voucher(self):
        if self.is_promotion_voucher:
            self.update({
                'tracking': 'serial',
                'type': 'product',
                'categ_id': self.env.ref('to_promotion_voucher.product_category_promotion_voucher')
                })