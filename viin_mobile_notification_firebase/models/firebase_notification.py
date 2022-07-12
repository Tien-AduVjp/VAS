import requests
import json

from odoo import models, api, tools, _

BASE_URL = 'https://fcm.googleapis.com/fcm/send'


class FirebaseNotification(models.Model):
    _inherit = 'mobile.notification'

    def _get_firebase_url(self):
        return BASE_URL

    def _prepare_firebase_request_data(self, list_tokens_silent, list_tokens_noisy):
        self.ensure_one()
        ConfigParams = self.env['ir.config_parameter'].sudo()
        key = ConfigParams.get_param('mobile.notify_auth_key', '')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key= {}'.format(key)
        }
        data_notification = self._prepare_data_to_open_in_view_window()
        data_notification.update({
            'id': self.id,
            'create_notification': True
        })

        notifcations = {
            'id': self.id,
            'body': self.body,
            'title': self.title,
            'content_available': True,
            'priority': 'high',
            'sound': 'default',
            'group': self._get_group_notification()[0],
            'tag': {
                'data': data_notification,
                'group': self._get_group_notification()[0],
                },
            'category': {
                'data': data_notification
                },
            }

        data_request_silent = {}
        data_request_noisy = {}
        # Silent remote push notification haven't field notification on root data
        if list_tokens_silent:
            data_notification['notification_type'] = 'silent'
            data_silent = data_notification.copy()
            data_silent['notification'] = notifcations
            data_request_silent.update({
                'registration_ids': list_tokens_silent,
                'data': data_silent
                })

        if list_tokens_noisy:
            data_notification['notification_type'] = 'noisy'
            data_noisy = data_notification.copy()
            data_request_noisy.update({
                'registration_ids': list_tokens_noisy,
                'notification': notifcations,
                'data': data_noisy
                })

        return headers, data_request_silent, data_request_noisy

    def _validate_firebase_response(self, data):
        """
        Method used to update notification detetail
        Because firebase return only list of string, we need to check each element in list,
            then map them with list notification line by index
        If a device receives a notification, the notification is considered successful
        @param {object} data incluce:
        @param {list} list_tokens_silent: list of token
        @param {object} response_silent: response from firebase for token silent
        @param {list} list_tokens_noisy: list of token
        @param {object} response_noisy: response from firebase for token noisy
        @param {records} notification_lines: list record notification line
        """
        self.ensure_one()
        notification_lines = data['notification_lines']

        resend = data['resend']
        list_tokens_silent = data['list_tokens_silent']
        response_silent = data['response_silent']
        list_tokens_noisy = data['list_tokens_noisy']
        response_noisy = data['response_noisy']

        result_firebase = {}
        if response_silent and response_silent.status_code == 200:
            status = response_silent.json()
            results = status['results']
            for index, result in enumerate(results):
                token = list_tokens_silent[index]
                result_firebase[token] = result
        if response_noisy and response_noisy.status_code == 200:
            status = response_noisy.json()
            results = status['results']
            for index, result in enumerate(results):
                token = list_tokens_noisy[index]
                result_firebase[token] = result
        for notify_line in notification_lines.sudo():
            message_id = ''
            error_message = _("Invalid Authorization key or Token does not exist")
            for device_token in notify_line.partner_id.mobile_token_ids:
                token = device_token.token
                if token in result_firebase:
                    # We need continue check result to unlink token was unRegistered
                    if 'message_id' in result_firebase[token]:
                        message_id = result_firebase[token]['message_id']
                        device_token.consecutive_error = 0
                    else:
                        error_message = result_firebase[token]['error']
                        if error_message in ("NotRegistered", "InvalidRegistration") or device_token.consecutive_error + 1 == 50:
                            device_token.unlink()
                        else:
                            device_token.consecutive_error += 1

            line_vals = {
                'state': 'success' if message_id else 'failed',
                'message_id': message_id,
                'error_message': '' if message_id else error_message,
            }
            if not message_id and resend:
                notify_max_retry = int(self.env['ir.config_parameter'].sudo().get_param('mobile.notify_max_retry', 5))
                line_vals['retried_count'] = notify_line.retried_count + 1
                if line_vals['retried_count'] >= notify_max_retry:
                    line_vals['state'] = 'cancelled'
            # Hide transaction serialization errors, which must be ignored because thread of channel seen will change state of this notify_line
            with tools.mute_logger('odoo.sql_db'):
                notify_line.write(line_vals)

    @api.model
    def _cancel_notification_firebase(self, title, list_token, key, notify_type, groups, notification_ids):
        """
        Method used to send request to firebase, mobile app will use this request to cancel notification on device
        @param {list} list_token: list token
        @param {list} groups: list group of notifications
        @param {list} ids: list id of mail.notification marked as read
        """
        data_notification = {
            'create_notification': False,
            'title': title,
            'notification_type': notify_type,
            'groups': groups,
            'ids': notification_ids,
            }
        data = {
            'registration_ids': list_token,
            'data': data_notification,
            'content_available': True,
            'apns-priority': 5
            }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key= {}'.format(key)
            }
        try:
            requests.post(BASE_URL, headers=headers, data=json.dumps(data), timeout=3)
        except:
            pass
