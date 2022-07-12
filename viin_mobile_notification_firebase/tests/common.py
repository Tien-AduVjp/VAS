from time import sleep
from requests.models import Response
import json
from odoo import fields

from odoo.addons.viin_mobile_notification.tests.common import MobileNotificationCommon
from odoo.addons.viin_mobile_notification_firebase.models.firebase_notification import BASE_URL


class MobileNotificationFirebaseCommon(MobileNotificationCommon):
    def setUp(self, number_partner=4):
        super(MobileNotificationFirebaseCommon, self).setUp(number_partner)
        self.setup_config()
        self.channel_1.channel_last_seen_partner_ids.mobile_notification = True
        self.channel_2.channel_last_seen_partner_ids.mobile_notification = True
        # Register token
        self.list_token_register = self.list_token.copy()
        # Add function rollback
        self.addCleanup(self.rollback_database)

    def _create_new_message_channel(self, user, channel, number_message):
        messages = self.env['mail.message']
        for i in range(number_message):
            messages += channel.with_user(user).message_post(
                body='notification',
                subtype_id=self.env.ref('mail.mt_comment').id,
                message_type='email',
            )
            # Need commit for user to another thread
            self.env.cr.commit()
        return messages

    def _create_new_mail_thread(self, user, record, partner_ids, number_message):
        messages = self.env['mail.message']
        for i in range(number_message):
            messages += record.with_user(user).message_post(
                body='mail thread',
                subtype_id=self.env.ref('mail.mt_comment').id,
                message_type='comment',
                partner_ids=partner_ids,
            )
            # Need commit to user another thread
            self.env.cr.commit()
        return messages

    def _check_request_firebase(self, url, headers, data, **kw):
        """ This method will check param of request
            If param is correct, it will return result like firebase"""
        sent_key = headers['Authorization']
        sent_key = sent_key[5:]

        self.assertEqual(url, BASE_URL, "viin_mobile_notification_firebase: wrong request url")
        self.assertEqual(sent_key, 'test_auth_key', "viin_mobile_notification_firebase: wrong request key")
        self.assertEqual(headers['Content-Type'], 'application/json',
                         "viin_mobile_notification_firebase: wrong request Content-Type")

        data = json.loads(data)
        registration_ids = data['registration_ids']
        self.assertNotEqual(len(registration_ids), 0, "viin_mobile_notification_firebase: data have no token")

        response = self._prepare_response_firebase(registration_ids)
        return response

    def _prepare_response_firebase(self, registration_ids):
        response = Response()
        response.status_code = 200
        response.reason = 'OK'
        response.url = BASE_URL

        success = 0
        failure = 0
        results = []
        for token in registration_ids:
            if token in self.list_token_register:
                success += 1
                results.append({
                    'message_id': 'message_id_success'
                })
            else:
                failure += 1
                results.append({
                    'error': 'NotRegistered'
                })
        content = {
            "multicast_id": str(fields.datetime.now()),
            "success": success,
            "failure": failure,
            "canonical_ids": 0,
            "results": results
        }
        response._content = str.encode(json.dumps(content))
        return response

    def rollback_database(self):
        self.channel_1.channel_message_ids.unlink()
        self.channel_2.channel_message_ids.unlink()
        self.device_tokens.unlink()

        self.list_partner -= self.env.ref('base.user_demo').partner_id
        self.list_partner -= self.env.ref('base.user_admin').partner_id
        self.list_partner.unlink()

        self.channel_1.unlink()
        self.channel_2.unlink()

        ConfigParams = self.env['ir.config_parameter'].sudo()
        ConfigParams.set_param('mobile.notify_provider', False)
        ConfigParams.set_param('mobile.notify_auth_key', False)
        ConfigParams.set_param('mobile.notify_type', False)
        ConfigParams.set_param('mobile.notify_max_retry', 5)
        ConfigParams.set_param('mobile.base_package', False)

        self.env.cr.commit()
