from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    print_app_desc_on_sale_order = fields.Boolean(string='App Description on PDF Quotation/Sale Order', default=True,
                                                help="If enabled, the description of Odoo App related to this product will be included in the PDF"
                                                " version of Quotations / Sales Orders")

