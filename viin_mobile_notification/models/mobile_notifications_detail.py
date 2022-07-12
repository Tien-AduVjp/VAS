from odoo import models, fields


class MobileNotificationsDetail(models.Model):
    # TODO: rename this to mobile.notification.line in master/14+
    _name = 'mobile.notification.detail'
    _description = """Notification detail"""
    
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    notification_id = fields.Many2one('mobile.notification', string='Notification ID', readonly=True)
    state = fields.Selection([
        ('new', 'New'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='new', required=True, readonly=True)

    retried_count = fields.Integer(readonly=True, string='Retried count')
    send_date = fields.Datetime(readonly=True, string='Send date')
    message_id = fields.Char(readonly=True, string='Message id')
    error_message = fields.Char(readonly=True, string='Error message')
