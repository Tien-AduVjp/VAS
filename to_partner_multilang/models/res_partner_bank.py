from odoo import fields, models


class ResPartnerPank(models.Model):
    _inherit = 'res.partner.bank'

    acc_holder_name = fields.Char(translate=True)
