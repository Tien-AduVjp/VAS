from odoo import models


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    def prepare_data_notify_increate_emoji(self, message, emoji_up, emoji_down):
        # Need add channel_ids for fix _handleChannelNotification
        return {
            'info': 'increate_emoji',
            'emoji_up': emoji_up,
            'emoji_down': emoji_down,
            'message_id': message.id,
            'partner_id': self.env.user.partner_id.id,
            'channel_ids': []
        }

    def notify_increate_emoji(self, message, emoji_up, emoji_down):
        self.ensure_one()
        notifications = []
        data = self.prepare_data_notify_increate_emoji(message, emoji_up, emoji_down)
        notifications.append([(self._cr.dbname, 'mail.channel', self.id), data])  # notify backend users
        notifications.append([self.uuid, data])  # notify frontend users
        self.env['bus.bus'].sendmany(notifications)
