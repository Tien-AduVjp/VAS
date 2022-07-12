from odoo import models, fields


class UtmSource(models.Model):
    _inherit = 'utm.source'

    available_for_affiliate_portal = fields.Boolean(string='Available For Affiliate Portal', default=True)
