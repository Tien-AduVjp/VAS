from odoo import fields, models


class res_currency(models.Model):
    _inherit = 'res.currency'

    currency_unit_label = fields.Char(translate=True)
