from odoo import models, fields


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    mobile_notify_provider = fields.Selection([], config_parameter='mobile.notify_provider', readonly=False)
    mobile_notify_type = fields.Selection([('noisy', 'Noisy'), ('silent', 'Silent')], config_parameter='mobile.notify_type', readonly=False)
    mobile_notify_auth_key = fields.Char(
        config_parameter='mobile.notify_auth_key', readonly=False)
    mobile_notify_max_retry = fields.Integer(
        default=5, config_parameter='mobile.notify_max_retry', string='Max retry count')
    mobile_base_package = fields.Char(string='Base package',
                                      config_parameter='mobile.base_package', readonly=False,
                                      help="If the models's notifications are not specified by the application, those notifications"
                                      " will be sent to the application whose package name is base package.")
