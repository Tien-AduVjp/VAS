from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gtm_enable = fields.Boolean(string='Enable Google Tag Manager', readonly=False,
                                related='website_id.gtm_enable')
    gtm_container_id = fields.Char(string='Google Tag Manager Container ID', help="Example: GTM-XXXX", readonly=False,
                                   related='website_id.gtm_container_id')
