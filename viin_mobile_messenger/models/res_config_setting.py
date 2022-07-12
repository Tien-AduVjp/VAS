from odoo import models, fields


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    mobile_messenger_package = fields.Char(string='Messenger package',
                                           config_parameter='mobile.messenger_package', readonly=False)
