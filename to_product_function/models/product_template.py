from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    function_id = fields.Many2one('product.function', string='Function', ondelete='restrict', index=True,
                                  help="Indicate the function of the product")
