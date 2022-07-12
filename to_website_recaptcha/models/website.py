from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class Website(models.Model):
    _inherit = 'website'

    recaptcha_site_key = fields.Char(string='ReCaptcha v2 Site Key')
    recaptcha_secret_key = fields.Char(string='ReCaptcha v2 Secret Key')
    recaptcha_site_key_v3 = fields.Char(string='ReCaptcha v3 Site Key')
    recaptcha_secret_key_v3 = fields.Char(string='ReCaptcha v3 Secret Key')
    recaptcha_score = fields.Float(string='Human Score', digits=(2, 1), default=0.3,
                                   help="Score returned by ReCaptcha v3 must be greater than or equal to this score to consider to be human.")

    @api.constrains('recaptcha_score')
    def _check_recaptcha_score(self):
        for r in self:
            if r.recaptcha_score < 0 or r.recaptcha_score > 1:
                raise ValidationError(_("Human Score is only in (0.0 - 1.0)"))
