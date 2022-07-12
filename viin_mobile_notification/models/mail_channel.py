from odoo import models, fields, api


class MailChanner(models.Model):
    _inherit = 'mail.channel'

    receive_mobile_notification = fields.Boolean(
        string='Receive mobile notifications',
        compute='_compute_receive_mobile_notification',
        help="Technical field to indicate if the current user gets mobile notifications for the current channel"
        )

    @api.depends('channel_last_seen_partner_ids.mobile_notification')
    def _compute_receive_mobile_notification(self):
        for r in self:
            # There should be one channel partner record for maximum but it's safe to take the very first one
            mail_channel_partner = r.channel_last_seen_partner_ids.filtered(
                lambda r: r.partner_id.id == self.env.user.partner_id.id
                )[:1]
            r.receive_mobile_notification = mail_channel_partner.mobile_notification

    def button_toggle_mobile_notification(self):
        for r in self:
            for mail_channel_partner in r.channel_last_seen_partner_ids.filtered(
                lambda r: r.partner_id.id == self.env.user.partner_id.id
                ):
                mail_channel_partner.mobile_notification = not mail_channel_partner.mobile_notification

    def channel_seen(self, last_message_id=None):
        """
        When user seen message on this channel, this function will cancel all mobile notification on this channel
        """
        self.ensure_one()
        if self.channel_message_ids.ids:
            all_messages = self.channel_message_ids
            mail_channel_partner = self.env['mail.channel.partner'].search([
                ('partner_id', '=', self.env.user.partner_id.id),
                ('channel_id', '=', self.id)
                ], limit=1)
            seen_message = mail_channel_partner.seen_message_id
            if seen_message and seen_message.id in all_messages.ids:
                last_index = all_messages.ids.index(seen_message.id)
            else:
                last_index = len(all_messages)
            messages = all_messages[:last_index]
            # If user is focusing this channel, the second thread will not create notification detail
            if messages:
                notifications = messages.sudo().mapped('mobile_notification_ids')
                if notifications:
                    notification_lines = self.env['mobile.notification.detail'].sudo().search([
                        ('partner_id', '=', self.env.user.partner_id.id),
                        ('notification_id', 'in', notifications.ids),
                        ('state', 'not in', ['success', 'cancelled'])])
                    if notification_lines:
                        # When a user read a message of a channel, the system considers all messages in that channel as read
                        # In this case we consider all notifications sent to mobile as successful
                        notification_lines.write({
                            'state': 'cancelled'
                        })
                        # Only need one request cancel to cancel all notification from a channel
                        notifications[0]._cancel()
        return super(MailChanner, self).channel_seen(last_message_id)
