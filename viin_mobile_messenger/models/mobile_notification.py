
from odoo import models, fields, api
from odoo.tools import safe_eval


class MobileNotification(models.Model):
    _inherit = 'mobile.notification'

    def _prepare_req_data(self, mobile_package, notify_type, resend):
        if self.mail_message_id.model == 'mail.channel':
            mobile_package_messenger = self.env['ir.config_parameter'].sudo().get_param('mobile.messenger_package', False)
            if mobile_package_messenger:
                return super(MobileNotification, self)._prepare_req_data(mobile_package_messenger, notify_type, resend)
        return super(MobileNotification, self)._prepare_req_data(mobile_package, notify_type, resend)
