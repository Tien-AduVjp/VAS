from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    collection_id = fields.Many2one('product.collection', related='product_tmpl_id.collection_id', store=True)
