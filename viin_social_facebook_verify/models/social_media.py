from odoo import models, fields


class SocialMedia(models.Model):
    _inherit = 'social.media'

    fb_exchange_token = fields.Text('User Exchange Token', help="you can get this token at https://developers.facebook.com/tools/explorer/")

    def action_token_60day(self):
        self.ensure_one()
        self._fb_exchange_token(self.fb_exchange_token)
