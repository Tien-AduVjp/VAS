from odoo import models, fields


class MailMessageEmoji(models.Model):
    _name = 'mail.message.emoji'
    _description = 'Message emoji'

    emoji_id = fields.Many2one('emoji', string='Emoji', readonly=True)
    message_id = fields.Many2one('mail.message', string='Message', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
