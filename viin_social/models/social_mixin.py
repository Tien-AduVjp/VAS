from odoo import models, _
from odoo.exceptions import UserError

class SocialMixin(models.AbstractModel):
    _name = 'social.mixin'
    _description = 'Social Mixin'

    def raise_http_error(self, response, request_url, title="An error has occurred", **kwargs):
        if not response.ok:
            msg = _(
                "%s: \n"
                "status code: %s \n"
                "response: \n %s \n"
                "%s"
            ) % (title, response.status_code, response.json(), kwargs)
            raise UserError(msg)

    def notify(self, message, type='info', title='Notify', sticky=False):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': type,
                'title': title,
                'message': message,
                'sticky': sticky,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
