from odoo import http
from odoo.http import request


class ControllerEmoji(http.Controller):
    @http.route('/message/increate/emoji', type='json', auth='user', methods=['POST'])
    def increate_emoji(self, message_id, emoji_name):
        """
        Method used to search emoji in table mail_message_emoji
        If emoji does exits, this method will increate number
        If emoji does not exits, this method will create a record
        @param {int} message_id: id of message
        @param {string} emoji_name: name of emoji
        """
        message = request.env['mail.message'].browse(message_id)
        if not message:
            return {'message': "Message id doesn't exist"}
        emoji = request.env['emoji'].search([('name', '=', emoji_name)], limit=1)
        partner_id = request.env.user.partner_id.id
        channel_id = message.res_id
        channel = request.env['mail.channel'].browse(channel_id)
        message_emoji = request.env['mail.message.emoji'].search([
            ('partner_id', '=', partner_id),
            ('message_id', '=', message_id),
        ], limit=1)
        emoji_up = emoji.name
        emoji_down = message_emoji.emoji_id.name
        if message_emoji:
            if message_emoji.emoji_id == emoji:
                message_emoji.unlink()
                emoji_up = False
            else:
                message_emoji.emoji_id = emoji
        else:
            emoji_down = False
            request.env['mail.message.emoji'].create({
                'partner_id': partner_id,
                'message_id': message_id,
                'emoji_id': emoji.id,
            })
        channel.notify_increate_emoji(message, emoji_up, emoji_down)
        return {'message': "Increate emoji success"}
