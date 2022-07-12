from odoo import models, api

class Channel(models.Model):
    _inherit = 'mail.channel'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        message = super(Channel, self).message_post(**kwargs)
        if len(self.channel_message_ids) == 1 and self.sudo().livechat_visitor_id:
            cookie_info = {
                    'folded': False,
                    'id': self.id,
                    'message_unread_counter': 0,
                    'operator_pid': [
                        self.livechat_operator_id.id,
                        self.livechat_operator_id.display_name
                    ],
                    'name': self.name,
                    'uuid': self.uuid,
                    'type': 'chat_request'
                }
            self.env['bus.bus'].sendone(self.sudo().livechat_visitor_id.access_token, cookie_info)
        return message
