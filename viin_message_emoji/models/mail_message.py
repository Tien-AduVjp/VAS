from odoo import models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    message_emoji_ids = fields.One2many('mail.message.emoji', 'message_id', string='Emojis')

    def message_format(self):
        """
        Method used to add object emoji and list emoji to message_values
        """
        message_values = super(MailMessage, self).message_format()
        if self[:1].model != 'mail.channel':
            return message_values
        list_emoji = self.env['emoji'].search_read([], ['name', 'emoji'])
        for message_value in message_values:
            message = self.browse(message_value['id'])
            message_emojis = message.message_emoji_ids
            message_emoji_obj = {}
            for message_emoji in message_emojis:
                name = message_emoji.emoji_id.name
                if name in message_emoji_obj:
                    message_emoji_obj[name]['number'] += 1
                else:
                    message_emoji_obj[name] = {
                        'number': 1,
                        'name': name,
                    }
            message_emoji_obj['total'] = len(message_emojis)
            message_value['emoji'] = message_emoji_obj
            message_value['list_emoji'] = list_emoji
        return message_values
