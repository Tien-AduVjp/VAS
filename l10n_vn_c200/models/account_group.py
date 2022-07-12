from odoo import models, fields


class AccountGroup(models.Model):
    _inherit = "account.group"

    name = fields.Char(translate=True)
