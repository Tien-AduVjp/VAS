from odoo import api, models


class Digest(models.Model):
    _inherit = 'digest.digest'

    @api.model
    def _replace_mobile_app_urls(self):
        from odoo.addons.viin_mobile import _replace_mobile_app_urls
        _replace_mobile_app_urls(self.env)
