from odoo import fields, models


class affiliate_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    vendor_app_comm_percent = fields.Float(string="Default Apps Commission Percentage", related='company_id.vendor_app_comm_percent', readonly=False)
    vendor_app_min_payout = fields.Monetary(string='Min. Payout', related='company_id.vendor_app_min_payout', readonly=False,
                                            currency_field='currency_id')
    dedicated_app_download_token_lifetime = fields.Boolean(related='company_id.dedicated_app_download_token_lifetime', readonly=False)
    app_download_token_lifetime = fields.Float(related='company_id.app_download_token_lifetime', readonly=False)
