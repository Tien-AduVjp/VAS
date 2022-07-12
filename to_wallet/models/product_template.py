from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wallet = fields.Boolean(string='Paid by Wallet', help="If checked, this product will be paid by wallet credit only.")
