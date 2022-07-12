from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    auto_product_default_code_generation = fields.Boolean(string='Auto Product Code Generation', default=False,
                                            help="Automatically generate and update product codes based on product name or"
                                            " the defined product code prefix and product sequence in the product category.")
