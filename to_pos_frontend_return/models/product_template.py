from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pos_returnable = fields.Boolean(string='Returnable in PoS', default=True,
                                    help="Check this field to make the product returnable in your Point of Sales")

