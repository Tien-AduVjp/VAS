from odoo import fields, models


class ResBank(models.Model):
    _inherit = 'res.bank'

    name = fields.Char(translate=True)
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
