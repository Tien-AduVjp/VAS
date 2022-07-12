from odoo import models, fields, api


class MailChanner(models.Model):
    _inherit = 'mail.channel'

    receive_mobile_notification = fields.Boolean(string='Receive notification on mobile', compute='_compute_receive_mobile_notification')

    @api.depends('channel_last_seen_partner_ids.mobile_notification')
    def _compute_receive_mobile_notification(self):
        partner = self.env.user.partner_id
        mail_channel_partners = self.channel_last_seen_partner_ids
        mail_channel_partner = mail_channel_partners.filtered(lambda r: r.partner_id.id == partner.id)[:1]
        self.receive_mobile_notification = mail_channel_partner.mobile_notification

    def button_toggle_mobile_notification(self):
        partner = self.env.user.partner_id
        mail_channel_partners = self.channel_last_seen_partner_ids
        mail_channel_partner = mail_channel_partners.filtered(lambda r: r.partner_id.id == partner.id)[:1]
        if mail_channel_partner.mobile_notification:
            mail_channel_partner.mobile_notification = False
        else:
            mail_channel_partner.mobile_notification = True

    def channel_seen(self):
        """
        When user seen message on this channel, this function will cancel all mobile notificaiton on this channel
        """
        self.ensure_one()
        if self.channel_message_ids.ids:
            all_messages = self.channel_message_ids
            mail_channel_partner = self.channel_last_seen_partner_ids.filtered(
                lambda r: r.partner_id.id == self.env.user.partner_id.id
                )
            old_seen_message_id = mail_channel_partner.seen_message_id.id
            if old_seen_message_id:
                last_index = all_messages.ids.index(old_seen_message_id)
            else:
                last_index = len(all_messages)
            messages = all_messages[:last_index]
            # If user is focusing this channel, the second thread will not creat notification detail
            if messages:
                notifications = messages.sudo().mobile_notification_id
                if notifications:
                    notification_details = notifications.notification_detail_ids.filtered(
                        lambda r: r.partner_id.id == self.env.user.partner_id.id
                        )
                    notification_details.write({
                        'state': 'success'
                    })
                    notifications[0]._cancel()
        return super(MailChanner, self).channel_seen()
