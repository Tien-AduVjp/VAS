from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_to_create_new_reason = fields.Boolean(string='Product Return',
                                                help='Allow to create new return reason in front-end', default=False)

