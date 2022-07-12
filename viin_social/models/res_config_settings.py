from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    receive_comment_notification = fields.Boolean(related='company_id.receive_comment_notification', readonly=False)
    receive_reactive_notification = fields.Boolean(related='company_id.receive_reactive_notification', readonly=False)
