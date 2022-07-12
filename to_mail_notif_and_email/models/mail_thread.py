from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, notify_by_email=True, **kwargs):
        recipients_data = super(MailThread, self)._notify_thread(message, msg_vals=msg_vals, notify_by_email=notify_by_email, **kwargs)
        self._notify_record_by_notify_force_from_email(message, recipients_data, msg_vals=msg_vals, **kwargs)
        return recipients_data

    def _notify_record_by_notify_force_from_email(self, message, recipients_data, msg_vals=False, **kwargs):
        """Notification method: inbox, force from email"""
        temp = []
        for p in recipients_data['partners']:
            if p['notif'] == 'email':
                p['notif'] = 'inbox'
                temp.append(p)

        if temp:
            recipients_data.update({'partners': temp})
            self._notify_record_by_inbox(message, recipients_data, msg_vals=msg_vals, **kwargs)
        return True
