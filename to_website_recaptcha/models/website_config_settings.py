from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recaptcha_site_key = fields.Char(
        string='ReCaptcha Site Key',
        related='website_id.recaptcha_site_key',
        readonly=False,
    )
    recaptcha_secret_key = fields.Char(
        string='ReCaptcha Secret Key',
        related='website_id.recaptcha_secret_key',
        readonly=False,
    )
    recaptcha_site_key_v3 = fields.Char(
        related='website_id.recaptcha_site_key_v3',
        readonly=False,
    )
    recaptcha_secret_key_v3 = fields.Char(
        related='website_id.recaptcha_secret_key_v3',
        readonly=False,
    )
    recaptcha_score = fields.Float(
        related='website_id.recaptcha_score',
        readonly=False,
    )
