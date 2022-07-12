from odoo import fields, models


class AffiliateConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    turn_off_affiliate_page_warning = fields.Boolean(related='company_id.turn_off_affiliate_page_warning', readonly=False)
