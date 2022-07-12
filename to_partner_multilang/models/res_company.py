from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    name = fields.Char(translate=True)
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
