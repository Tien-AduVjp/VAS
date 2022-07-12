from odoo import models, fields


class UtmMedium(models.Model):
    _inherit = 'utm.medium'

    available_for_affiliate_portal = fields.Boolean(string='Available For Affiliate Portal', default=True)
