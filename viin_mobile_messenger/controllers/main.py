import re
from odoo import http, _
from odoo.http import request

class ControllerMobileMessenger(http.Controller):

    @http.route('/mobile/messenger/listchannel', type='json', auth='user', methods=['POST'])
    def list_channel(self):
        partner_id = request.env.user.partner_id.id
        channels = request.env['mail.channel'].search([('channel_partner_ids', 'in', [partner_id])])
        channel_list = []
        cleanr = re.compile('<.*?>')
        channel_message = {}
        for channel in channels:
            last_message = channel.message_ids[:1]
            last_message_create_date = last_message.create_date
            last_message_is_outgoing = last_message.author_id.id == partner_id
            partner_status = False
            last_message_content = ''

            if last_message:
                if last_message.body != '':
                    last_message_content = re.sub(cleanr, '', last_message.body)
                elif last_message.attachment_ids:
                    last_message_content = _("Attachment file")
                partner_send = last_message.author_id
            if channel.is_chat:
                members = channel.channel_partner_ids
                partner = members.filtered(lambda r: r.id != partner_id)
                partner_status = partner.im_status
                image_128 = partner.image_128
                display_name = partner.name
            else:
                if partner_send:
                    last_message_content = "%s: %s" % (partner_send.name, last_message_content)
                image_128 = channel.image_128
                display_name = channel.display_name

            channel_obj = {
                'channel_id': channel.id,
                'display_name': display_name,
                'image_128': image_128,
                'is_chat': channel.is_chat,
                'description': channel.description,
                'last_message': last_message_content,
                'last_message_is_outgoing': last_message_is_outgoing,
                'last_message_date': last_message_create_date,
                'partner_status': partner_status,
                'counter_message_unread': channel.message_unread_counter,
                'public': channel.public,
            }
            channel_message[channel.id] = {
                'list_message': [],
                'can_load_more': True
            }
            channel_list.append(channel_obj)

        return {'channel_list': channel_list, 'channel_message': channel_message}

    @http.route('/mobile/messenger/channelmessage', type='json', auth='user', methods=['POST'])
    def channel_message(self, channel_id, last_message_id=False):
        partner_id = request.env.user.partner_id.id
        channel = request.env['mail.channel'].search([('id', '=', channel_id)])
        all_messages = channel.message_ids.filtered(lambda r: r.message_type in ('comment', 'notification'))
        if last_message_id:
            if last_message_id not in all_messages.ids:
                messages = all_messages[:20]
            else:
                last_message_index = all_messages.ids.index(last_message_id)
                if last_message_index + 1 >= len(all_messages):
                    return {}
                messages = all_messages[last_message_index + 1 : last_message_index + 21]
        else:
            return {}
        list_message = []
        cleanr = re.compile('<.*?>')
        for message in messages:
            body = re.sub(cleanr, '', message.body)
            author_id = message.author_id
            attachments = message.attachment_ids
            message_infor = {
                'body': body,
                'id': message.id,
                'is_outgoing': author_id.id == partner_id,
                'attachment_ids': attachments.ids,
                'file_names': attachments.mapped('name'),
                'file_types': attachments.mapped('mimetype'),
                'partner_create': author_id.id,
                'is_first_message': message.id == all_messages[-1:].id,
                'date': message.date,
            }
            list_message.append(message_infor)
        if not all_messages:
            can_load_more = False
        else:
            can_load_more = messages[-1].id != all_messages[-1:].id

        channel_message = {'list_message': list_message, 'can_load_more': can_load_more}
        return channel_message

    @http.route('/mobile/messenger/channelinfo', type='json', auth='user', methods=['POST'])
    def channel_info(self, channel_id):
        partner_id = request.env.user.partner_id.id
        channel = request.env['mail.channel'].search([('id', '=', channel_id)])
        seen_message_id = False
        fetched_message_id = False
        if channel.is_chat:
            for seen_partner_info in channel.channel_info()[0]['seen_partners_info']:
                if seen_partner_info['partner_id'] != partner_id:
                    seen_message_id = seen_partner_info['seen_message_id']
                    fetched_message_id = seen_partner_info['fetched_message_id']
        obj_members = {}
        list_members = []
        for member in channel.channel_partner_ids:
            member_infor = {
                'display_name': member.name,
                'image_128': member.image_128,
                'id': member.id,
                'email': member.email,
                'im_status': member.im_status,
            }
            obj_members[member.id] = member_infor
            list_members.append(member_infor)

        channel_info = {
            'is_chat': channel.is_chat,
            'fetched_message_id': fetched_message_id,
            'seen_message_id': seen_message_id,
            'members': obj_members,
            'list_member_ids': channel.channel_partner_ids.ids,
            'list_members': list_members,
            'list_image': channel.channel_partner_ids.mapped('image_128'),
            'description': channel.description,
            'id': channel.id,
            'name': channel.name,
            'image_128': channel.image_128,
            'is_subscribed': channel.is_subscribed
        }
        return channel_info
