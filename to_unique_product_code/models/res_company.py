from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    check_unique_product_default_code = fields.Boolean(string='Checking unique Product Internal Reference', default=False,
                                                       help="The creation of duplicated Product Internal Reference are not allowed")
