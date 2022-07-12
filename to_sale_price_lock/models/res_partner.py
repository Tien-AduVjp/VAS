from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    property_product_pricelist = fields.Many2one(tracking=True)
