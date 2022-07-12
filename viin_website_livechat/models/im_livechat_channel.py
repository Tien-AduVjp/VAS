from odoo import models, fields


class ImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    button_text = fields.Char(translate=True)
    default_message = fields.Char(translate=True)
    input_placeholder = fields.Char(translate=True)
