from odoo import fields, models


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    balance_carry_forward_journal_id = fields.Many2one(related='company_id.balance_carry_forward_journal_id', readonly=False)
