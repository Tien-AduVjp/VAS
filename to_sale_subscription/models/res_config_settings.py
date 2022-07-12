from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_subscription_rating = fields.Boolean("Use Rating on Subscription", implied_group='to_sale_subscription.group_subscription_rating')
