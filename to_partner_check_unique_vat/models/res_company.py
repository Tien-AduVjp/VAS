from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    check_unique_vat = fields.Boolean(string='Checking unique VAT of partner', default=False,
                                      help="The creation of duplicated tax code contacts are not allowed")
