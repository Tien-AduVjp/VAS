from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender',
    )
