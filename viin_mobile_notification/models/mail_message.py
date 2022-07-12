import re
import logging

from odoo import models, fields
_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    mobile_notification_ids = fields.One2many('mobile.notification', 'mail_message_id', string='Mobile Notifications')

    def set_message_done(self):
        res = super(MailMessage, self).set_message_done()
        self._cancel_mobile_notification()
        return res

    def _create_mail_channel_mobile_notifications(self, **kwargs):
        """
        Method used to create notifications for model 'mail.channel'
        """
        self.ensure_one()
        if self.model != 'mail.channel':
            return self.env['mobile.notification']

        vals_list = []
        for channel in self.channel_ids:
            partners_to_need_send_notification = self.env['res.partner']
            domain = [
                ('channel_id', '=', channel.id),
                ('partner_id.active', '=', True),
                ('partner_id.user_ids', '!=', False),
                ('partner_id', '!=', self.author_id.id),
                ('seen_message_id', '!=', self.id)
            ]
            if channel.channel_type == 'channel':
                domain.append(('mobile_notification', '=', True))
            # Need sudo, Bz public user can't read mail.channel.partner
            partners_to_need_send_notification = self.env['mail.channel.partner'].sudo().search(domain).mapped('partner_id')

            if not partners_to_need_send_notification:
                continue

            cleanr = re.compile('<.*?>')
            body = re.sub(cleanr, '', self.body)
            if channel.channel_type == 'chat':
                title = self.author_id.sudo().name or ''
            else:
                title = "# %s" % (self.record_name)
                if self.sudo().author_id.name:
                    body = "%s: %s" % (self.sudo().author_id.name, body)

            notification_vals = self._prepare_mobile_notification_vals(
                title,
                body,
                partners_to_need_send_notification,
                )
            vals_list.append(notification_vals)
        return self.env['mobile.notification'].sudo().create(vals_list)

    def _cancel_mobile_notification(self):
        """
        When user mark as done a action, this function will find list goup of notification of this message
        then send request to cancel notification on mobile device
        This method will change state of mobile_notificaiton_datail to cancelled
        """
        notifications = self.env['mobile.notification'].sudo().search([('mail_message_id', 'in', self.ids)])
        notification_lines = self.env['mobile.notification.detail'].sudo().search([
            ('partner_id', '=', self.env.user.partner_id.id),
            ('notification_id', 'in', notifications.ids),
            ('state', 'not in', ['success', 'cancelled'])])
        notification_lines.write({
            'state': 'cancelled'
        })
        if notifications:
            notifications[:1]._cancel(notifications._get_group_notification(), notifications.ids)

    def _prepare_mobile_notification_vals(self, title, body, partners):
        notification_detail_cmd = [(0, 0, partner._prepare_mobile_notification_detail_vals()) for partner in partners]
        if not notification_detail_cmd:
            return {}
        return {
            'title': title,
            'body': body,
            'state': 'new',
            'mail_message_id': self.id,
            'line_ids': notification_detail_cmd
        }
