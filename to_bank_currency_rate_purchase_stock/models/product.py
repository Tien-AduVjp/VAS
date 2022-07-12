from odoo import models


class Product(models.Model):
    _inherit = "product.product"
    
    def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
        return super(Product, self)._select_seller(partner_id=partner_id, quantity=quantity, date=date, uom_id=uom_id, params=params) \
                                    .with_context(exchange_type='sell_rate')
