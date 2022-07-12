from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    function_id = fields.Many2one('product.function', related='product_tmpl_id.function_id', store=True)
