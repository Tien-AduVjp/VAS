from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _used_in_bom(self):
        bom_products = self.browse()
        if not self:
            return bom_products
        boms = self.bom_line_ids.bom_id
        products = boms.product_id | boms.product_tmpl_id.product_variant_ids
        products |= products._used_in_bom()
        return products

    def _use_boms(self):
        bom_products = self.browse()
        if not self:
            return bom_products
        boms = self.bom_ids | self.product_variant_ids.bom_ids
        products = boms.bom_line_ids.product_id
        products |= products._use_boms()
        return products
