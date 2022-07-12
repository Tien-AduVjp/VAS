
import threading
import re
import logging

from concurrent.futures import ThreadPoolExecutor
from time import sleep

from odoo import models, api, _
from odoo.addons.to_base.models.to_base import after_commit

executor = ThreadPoolExecutor(max_workers=5)
_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = ['mail.thread']

    def _notify_thread(self, message, msg_vals=False, notify_by_email=True, **kwargs):
        """
        When odoo system create notification, this function will create notification for mobile
        This function will create new thread to create request
        """
        rdata = super(MailThread, self)._notify_thread(
            message,
            msg_vals=msg_vals,
            notify_by_email=notify_by_email,
            **kwargs
        )
        self._notify_by_mobile_phone(message, rdata.get('partners', False))
        return rdata

    @after_commit
    def _notify_by_mobile_phone(self, message, partners):
        # TODO: R&D for using cron to send mobile notifications in queue instead of using ThreadPoolExecutor
        vals = {
            'message': message,
            'partners': partners
            }
        if getattr(threading.main_thread(), 'testing', False) or self.env.registry.in_test_mode():
            with ThreadPoolExecutor(max_workers=1) as ex:
                ex.submit(self._create_mobile_notifications, vals)
        else:
            executor.submit(self._create_mobile_notifications, vals)

    def _create_mobile_notifications(self, data):
        # As this method is in a new thread, a new cursor is required because the old one may be closed already
        with api.Environment.manage(), self.pool.cursor() as cr:
            try:
                env = self.env(cr=cr)
                # Will not create notifications without mobile notification provider
                if not env['ir.config_parameter'].sudo().get_param('mobile.notify_provider', False):
                    return
                message = data['message'].with_env(env)
                partners_data = data['partners']
                if partners_data and message.model != 'mail.channel':
                    partner_ids = [partner_data['id'] for partner_data in partners_data]
                    partners = env['res.partner'].browse(partner_ids).sudo().filtered(lambda p: p.user_ids)
                    notifications = self.with_env(env)._create_mail_thread_mobile_notification(message, partners)
                else:
                    # sleep 5 seconds is needed as when user is online and focusing on this channel,
                    # message will mark as read.
                    # We won't send notification for that user.
                    # TODO: master/15+ put this 5 seconds in config settings instead of hard coded here
                    sleep(5)
                    notifications = message._create_mail_channel_mobile_notifications()
                if notifications:
                    notifications.sudo()._send()
            except Exception as e:
                _logger.error("Mobile Notification Error: %s", str(e))

    def _create_mail_thread_mobile_notification(self, message, partners, **kwargs):
        """
        Method used to create notifications for models 'mail.thread'
        """
        if not partners:
            return
        message_format = message.message_format()

        if isinstance(self, self.env['mail.thread'].__class__):
            body = message.subject or (message.record_name and _('Re: %s') % message.record_name)
            title = self._description
        else:
            cleanr = re.compile('<.*?>')
            body = re.sub(cleanr, '', message_format[0].get('body', False) or '')
            title = "%s: %s" % (self._description or self._name, message.name_get()[0][1])

        if message.sudo().tracking_value_ids:
            subtype_description = message_format[0].get('subtype_description', False) or ''
            tracking_values = message_format[0]['tracking_value_ids'] or []
            bodys_list = []
            for tracking_value in tracking_values:
                new_value = tracking_value.get('new_value', False) or ''
                bodys_list.append('%s ➞ %s' % (subtype_description, new_value))
            body = '\n'.join(bodys_list)

        # Prepend author name to the body if available
        author_name = message.sudo().author_id.name
        if author_name:
            body = "%s: %s" % (author_name, body)

        mobile_notification_vals = message._prepare_mobile_notification_vals(
            title,
            body,
            partners,
            )
        return self.env['mobile.notification'].sudo().create(mobile_notification_vals)
