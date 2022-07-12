from odoo import models, api, fields
from odoo.osv import expression


class MailMessage(models.Model):
    _inherit = 'mail.message'

    mobile_notification_id = fields.Many2one('mobile.notification', string='Mobile notification')

    def set_message_done(self):
        """
        When user mark as done a action, this function will find list goup of notification of this message
        then send request to cancel notification on mobile device
        This method will change state of mobile_notificaiton_datail to success
        """
        super(MailMessage, self).set_message_done()
        notifications = self.sudo().mobile_notification_id
        partner_id = self.env.user.partner_id.id
        notification_details = notifications.notification_detail_ids.filtered(
            lambda r: r.partner_id.id == partner_id
            )
        notification_details.state = 'success'
        if notifications:
            groups = notifications.mapped('group')
            # merge item inside list
            groups = list(set(groups))
            notify_ids = notifications.ids
            notifications[:1]._cancel(groups, notify_ids)
        return

    @api.model
    def mark_all_as_read(self, domain=None):
        """
        When all message is marked as done, this function will find list goup of notification of them
        then send request to cancel notification on mobile device
        This method will change state of mobile_notificaiton_datail to success
        """
        partner_id = self.env.user.partner_id.id
        notif_domain = [
            ('res_partner_id', '=', partner_id),
            ('is_read', '=', False)
            ]

        if domain:
            messages_ids = self.search(domain).ids
            notif_domain = expression.AND([notif_domain, [('mail_message_id', 'in', messages_ids)]])

        mail_notifications = self.env['mail.notification'].sudo().search(notif_domain)
        mail_messages = mail_notifications.mail_message_id
        notifications = mail_messages.sudo().mobile_notification_id
        partner_id = self.env.user.partner_id.id
        notification_details = notifications.notification_detail_ids.filtered(
            lambda r: r.partner_id.id == partner_id
            )
        notification_details.write({
            'state': 'success'
        })
        if notifications:
            groups = notifications.mapped('group')
            # merge item inside list
            groups = set(groups)
            groups = list(groups)
            notifications[:1]._cancel(groups)
        return super(MailMessage, self).mark_all_as_read(domain=domain)
