from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_creditor_price_difference_categ = fields.Many2one(tracking=True)
