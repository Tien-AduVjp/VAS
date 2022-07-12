from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    notification_type = fields.Selection(help="Policy on how to handle Chatter notifications:\n"
                                         "- Handle by Emails: notifications appear in your Odoo Inbox and are sent to your email at the same time\n"
                                         "- Handle in Odoo: notifications appear in your Odoo Inbox")
