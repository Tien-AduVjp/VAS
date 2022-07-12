from odoo import models, fields


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    mobile_notify_provider = fields.Selection(selection_add=[('firebase', 'Firebase')])
