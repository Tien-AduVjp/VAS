from odoo import models, fields


class MobileNotificationsDetail(models.Model):
    # TODO: rename this to mobile.notification.partner in master/15+
    _name = 'mobile.notification.detail'
    _description = "Notification Partner"

    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True, ondelete='cascade', index=True)
    notification_id = fields.Many2one('mobile.notification', string='Notification ID', readonly=True,
                                      ondelete='cascade', index=True, required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='new', required=True, readonly=True, index=True,
        help="* Status of notifications sent to a specific device, it is used to calculate whether system should be sent notification to that device again?"
        "\n* new: notification have been created and not yet sent, details with this status will be sent back by cron"
             "\n* success: Sent successfully"
             "\n* failed: Sent failed, details with this status will be sent back by cron"
             "\n* cancelled: If the number of resends is greater than 'Retried Count', the status will be cancelled"
    )

    retried_count = fields.Integer(readonly=True, string='Retried Count',
                                   help="Maximum number of resends")
    # TODO: master/15+ replace send_date by create_date
    send_date = fields.Datetime(readonly=True, string='Send Date')
    message_id = fields.Char(readonly=True, string='Notification ID on Device',
                             help="Message-ID returned by the notification service providers on successful sent, it also the id of the notification on the device")
    error_message = fields.Char(readonly=True, string='Error Message',
                                help="Message-Error returned by the notification service providers on failed sent, used to check the cause of failed sent")
