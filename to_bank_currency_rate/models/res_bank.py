from odoo import models, fields


class ResBank(models.Model):
    _inherit = "res.bank"

    auto_rate_update = fields.Boolean(string='Auto Currency Rates Update')
    auto_rate_update_provider = fields.Selection([], string='Auto Currency Rates Update Service Provider')
