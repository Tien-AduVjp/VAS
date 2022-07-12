from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    receive_comment_notification = fields.Boolean(string='Receive Comment Notification', default=True,
                                                  help="Receive comment notifications from social networks")
    receive_reactive_notification = fields.Boolean(string='Receive Reactive Notification', default=True,
                                                   help="Receive notifications of post reactions from social networks")
