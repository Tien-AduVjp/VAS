from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loyalty_points_reward_policy = fields.Selection(string='Loyalty Points Reward Policy', related='company_id.loyalty_points_reward_policy', readonly=False)
