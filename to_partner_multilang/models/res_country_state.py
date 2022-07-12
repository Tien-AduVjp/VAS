from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    name = fields.Char(translate=True)
