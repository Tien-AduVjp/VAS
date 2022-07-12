import re
from functools import partial

from odoo import models, api


class MailThread(models.AbstractModel):
    _inherit = ['mail.thread']

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        """
        When odoo system create notification, this function will create notification for mobile
        This function will create new thread to create request
        """
        rdata = super(MailThread, self)._notify_thread(
            message,
            msg_vals=msg_vals,
            **kwargs
        )
        # will not create notification before setup mobile notification
        if self.env['ir.config_parameter'].sudo().get_param('mobile.notify_provider', False):
            self._mobile_notification(message, rdata.get('partners', False))
        return rdata

    def _mobile_notification(self, message, partners):
        if partners and message.model != 'mail.channel':
            notifications = self._create_mail_thread_mobile_notification(message, partners)
        else:
            notifications = self._create_mail_channel_mobile_notifications(message)
        if notifications:
            self.env.cr.after('commit', partial(self.send_notification_mobile,notifications=notifications))
    
    def send_notification_mobile(self, notifications):
        # Make sure Environment exists
        with api.Environment.manage():
            notifications.sudo()._send()
             
    def _create_mail_thread_mobile_notification(self, message, partners, **kwargs):
        """
        Method used to create notifications for models 'mail.thread'
        """
        partner_ids = []
        for partner in partners:
            partner_ids.append(partner['id'])
        partners = self.env['res.partner'].browse(partner_ids).exists()

        if not partners:
            return

        data = {'res_model': message.model, 'res_id': message.res_id}
        group = {message.model}, {message.res_id}

        cleanr = re.compile('<.*?>')
        message_format = message.message_format()

        if isinstance(self, self.env['mail.thread'].__class__):
            body = message.subject
            title = self._description
        else:
            body = re.sub(cleanr, '', message_format[0].get('body', False) or '')
            title = (self._description or self._name) + ': ' + message.name_get()[0][1]

        if message.sudo().tracking_value_ids:
            subtype_description = message_format[0].get('subtype_description', False) or ''
            tracking_values = message_format[0]['tracking_value_ids'] or []
            bodys_list = []
            for tracking_value in tracking_values:
                new_value = tracking_value.get('new_value', False) or ''
                bodys_list.append('%s ➞ %s' % (subtype_description, new_value))
            body = '\n'.join(bodys_list)
        if message.author_id.name:
            body = message.author_id.name + ": " + body

        notification = self.env['mobile.notification'].sudo().create(
            self._prepare_mobile_notification_vals(
                title,
                body,
                partners,
                data,
                message,
                group
            )
        )
        message.write({'mobile_notification_id': notification.id})
        return notification

    def _create_mail_channel_mobile_notifications(self, message, **kwargs):
        """
        Method used to create notifications for model 'mail.channel'
        """
        notifications = self.env['mobile.notification']
        for channel in message.channel_ids:
            partners_to_need_send_notification = self.env['res.partner']

            for r in channel.channel_last_seen_partner_ids:
                if r.partner_id.active and r.partner_id.id != message.author_id.id and (r.fetched_message_id.id != r.seen_message_id.id or r.fetched_message_id.id != message.id):
                    if channel.channel_type == 'channel':
                        if r.mobile_notification:
                            partners_to_need_send_notification |= r.partner_id
                    else:
                        partners_to_need_send_notification |= r.partner_id
            if not partners_to_need_send_notification:
                continue

            data = {'action': self.env.ref('mail.action_discuss').id, 'res_model': message.model, 'active_id': channel.id}
            group = {message.model}, {channel.id}

            cleanr = re.compile('<.*?>')
            if channel.channel_type == 'chat':
                title = message.author_id.name or ''
                body = re.sub(cleanr, '', message.body)
            else:
                title = "# " + message.record_name
                if message.author_id.name:
                    body = message.author_id.name + ": " + re.sub(cleanr, '', message.body)
                else:
                    body = re.sub(cleanr, '', message.body)
            notification = self.env['mobile.notification'].sudo().create(
                self._prepare_mobile_notification_vals(
                    title,
                    body,
                    partners_to_need_send_notification,
                    data,
                    message,
                    group
                )
            )
            message.write({'mobile_notification_id': notification.id})
            notifications += notification
        return notifications

    def _prepare_mobile_notification_vals(self, title, body, partners, data, mail_message, group):
        notification_detail_cmd = [(0, 0, partner._prepare_mobile_notification_detail_vals()) for partner in partners]
        if not notification_detail_cmd:
            return {}
        return {
            'title': title,
            'body': body,
            'data': data,
            'state': 'new',
            'mail_message_id': mail_message.id,
            'group': group,
            'notification_detail_ids': notification_detail_cmd
        }
