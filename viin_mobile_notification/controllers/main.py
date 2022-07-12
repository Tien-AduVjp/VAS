from datetime import datetime
from odoo import _, http
from odoo.http import request


class ControllerNotifications(http.Controller):
    @http.route('/mobile/notifications/add/token', type='json', auth='user', methods=['POST'])
    def add_token(self, token, platform, package_name):
        """
        Method used to save token and token infomation when user login success.
        It will check if token exists in table 'mobile.device.token' or not? 
        If token does exists, it will check the other fields, if all fields are duplicate will return the message 'Token already exists'. 
        If only 1 field is distinct, it will change the information to that token.
        If token does  exists, this function will add new record
        @param {string} token: a devices token. Each of the above applications installed on 1 device will have 1 token.
            We can refresh token.
        @param {string} platform: android or ios
        @return {string} package_name: name of project
        """
        partner = request.env.user.partner_id
        device_token = request.env['mobile.device.token'].sudo().search([('token', '=', token)])
        if device_token.partner_id.id == partner.id and device_token.platform == platform and device_token.package_name == package_name:
            data = {'status': 200,
                    'message': "Token already exists"}
            return data
        elif device_token:
            device_token.partner_id = partner
            device_token.platform = platform
            device_token.package_name = package_name
            data = {'status': 200, 'message': "Add success"}
            return data
        else:
            vals = {
                'token': token,
                'partner_id': partner.id,
                'platform': platform,
                'package_name': package_name
            }
            request.env['mobile.device.token'].sudo().create(vals)
            data = {'status': 200, 'message': "Add success"}
            return data

    @http.route('/mobile/notifications/logout', type='json', auth='user', methods=['POST'])
    def logout(self, token):
        """
        Method used to delete token when user logout mobile app.
        It will check if token exists in table 'mobile.device.token' or not? 
        If exists, will unlink this token in table 'mobile.device.token' then return message "Delete success"
        If token does not exists, this function will return message "Token does not exist"
        @param {string} token: a devices token.
        """
        partner = request.env.user.partner_id
        device_token = request.env['mobile.device.token'].sudo().search([
            ('partner_id', '=', partner.id), ('token', '=', token)])
        if device_token:
            device_token.sudo().unlink()
            data = {'status': 200, 'message': "Delete success"}
            return data
        else:
            data = {'status': 200, 'message': "Token does not exist"}
            return data

    @http.route('/mobile/notifications/notification_info', type='json', auth='user')
    def mobile_get_info_notification(self, mobile_channel_seens, mobile_inbox_date):
        """
        Method used to get notification information and then return it.
        It will search for messages marked as viewed since most recent call up to now; and current number badge
        It will return:
            last id of messages marked as viewed of all channel,  
            current time, 
            list group of notifications need cancel on mobile device,
            number badge,
            mobile_inbox_ids: list id of mail inbox was marked as seen
        @param {object} mobile_channel_seens: contains the id of messages marked as viewed of  most recent call
        @param {date} mobile_inbox_date: time of most recent call
        """
        notify_groups = []
        partner_id = request.env.user.partner_id.id
        channels = request.env['mail.channel'].search([('channel_partner_ids', 'in', partner_id)])

        notify_groups_channel, mobile_channel_seens = self._check_mobile_channel_seen(partner_id, channels, mobile_channel_seens)
        notify_inbox_groups, mobile_inbox_date, mobile_inbox_ids = self._check_mobile_last_inbox(partner_id, mobile_inbox_date)
        notify_groups = notify_inbox_groups + notify_groups_channel
        # merge item inside list
        notify_groups = set(notify_groups)
        notify_groups = list(notify_groups)

        unread_counters, mail_inbox_counters = self._get_number_badge(partner_id, channels)

        result = {
            'unread_counters': unread_counters or 0,
            'mail_inbox_counters': mail_inbox_counters or 0,
            'notify_groups': notify_groups,
            'mobile_channel_seens': mobile_channel_seens,
            'mobile_inbox_date': mobile_inbox_date,
            'mobile_inbox_ids': mobile_inbox_ids,
        }
        return result

    def _check_mobile_channel_seen(self, partner_id,  channels, mobile_channel_seens):
        """
        Method used to search for messages marked as viewed since most recent call up to now of all channel.
        It will return:
            last id of messages marked as viewed of all channel,  
            list group of notifications need cancel on mobile device,
        @param {int} partner_id: partner id
        @param {list} channels: List of channels where current partner is a member
        @param {object} mobile_channel_seens: contains the id of messages marked as viewed of  most recent call
        """
        message_seen_ids = []
        notify_groups_channel = []
        mobile_notification = request.env['mobile.notification'].sudo()
        mail_channel_partners = request.env['mail.channel.partner'].search_read(
            [('partner_id.id', '=', partner_id), ('channel_id.id', 'in', channels.ids)],
            ['seen_message_id', 'channel_id'])
        channel_partners = {}
        for mail_channel_partner in mail_channel_partners:
            if mail_channel_partner['seen_message_id']:
                channel_partners[mail_channel_partner['channel_id'][0]] = mail_channel_partner['seen_message_id'][0]

        for channel in channels:
            if channel.id in channel_partners:
                all_message = channel.message_ids
                partner_last_seen_id = channel_partners[channel.id]
                partner_last_seen_index = all_message.ids.index(partner_last_seen_id)
                mobile_seen_id = mobile_channel_seens.get(str(channel.id), False)
                if mobile_seen_id in all_message.ids:
                    last_seen_index = all_message.ids.index(mobile_seen_id)
                else:
                    last_seen_index = len(all_message)-1
                if partner_last_seen_index < last_seen_index:
                    message_seen_ids += (all_message[partner_last_seen_index:last_seen_index].ids)
                mobile_channel_seens[str(channel.id)] = partner_last_seen_id

        notifications = mobile_notification.search([('mail_message_id.id', 'in', message_seen_ids)])
        if notifications:
            notify_groups_channel = notifications.mapped('group')
        return notify_groups_channel, mobile_channel_seens

    def _check_mobile_last_inbox(self, partner_id, mobile_inbox_date):
        """
        Method used to search for messages marked as viewed since most recent call up to now of mail inbox.
        It will return:
            current time,  
            list group of notifications need cancel on mobile device,
        @param {int} partner_id: partner id
        @param {date} mobile_inbox_date: time of most recent call
        """
        mail_notification = request.env['mail.notification']
        all_mail_notification = mail_notification.search([
            ('res_partner_id', '=', partner_id),
            ('is_read', '=', True),
            ('read_date', '>=', mobile_inbox_date),
            ('notification_status', '=', 'sent')
        ])
        notify_inbox_groups = []
        mobile_inbox_date = datetime.now()
        mobile_inbox_ids = []
        if all_mail_notification:
            mail_messages = all_mail_notification.mail_message_id
            mail_notifications = request.env['mobile.notification'].sudo().search([('mail_message_id.id', 'in', mail_messages.ids)])
            notify_inbox_groups = mail_notifications.mapped('group')
            mobile_inbox_ids = mail_notifications.ids
        return notify_inbox_groups, mobile_inbox_date, mobile_inbox_ids

    def _get_number_badge(self, partner_id, channels):
        """
        Method used to search for messages marked as unread then count them.
        It will return:
            number message marked as unread,
            number mail inbox marked as unread,
        @param {int} partner_id: partner id
        @param {list} channels: List of channels where current partner is a member
        """
        # This function return number of badge
        message_unread_counters = channels.mapped('message_unread_counter')
        unread_counters = sum(message_unread_counters)

        mail_inbox = request.env['mail.notification'].search([('is_read', '=', False), ('res_partner_id.id', '=', partner_id)])
        mail_inbox_counters = len(mail_inbox)

        return unread_counters, mail_inbox_counters
