from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    landed_cost_journal_id = fields.Many2one('account.journal', related='company_id.landed_cost_journal_id', readonly=False)
