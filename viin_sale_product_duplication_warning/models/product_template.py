from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ignore_product_duplication_warning = fields.Boolean(string='Ignore Product Duplication Warning on Quotation/Sales Orders',
                                              help="If enabled, duplication warning for this product on the same quotation/sales order will be ignored.\n"
                                              "If this product is usually expected to appear more than 1 times in the same quotation/sales order,"
                                              " you should enable this option.")
