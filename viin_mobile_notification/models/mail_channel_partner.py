from odoo import models, fields


class MailChannelPartner(models.Model):
    _inherit = 'mail.channel.partner'

    mobile_notification = fields.Boolean(string='Receive Mobile Notification', readonly=True, default=True)
