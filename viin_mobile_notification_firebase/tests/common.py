from time import sleep
from requests.models import Response
import json
from odoo import fields

from odoo.addons.viin_mobile_notification.tests.common import MobileNotificationCommon
from odoo.addons.viin_mobile_notification.models.mobile_notification import get_count_worker_request, get_count_worker_update_database
from odoo.addons.viin_mobile_notification_firebase.models.firebase_notification import BASE_URL


class MobileNotificationFirebaseCommon(MobileNotificationCommon):
    def setUp(self, number_partner=4):
        self.env['res.users'].search([('login', '=', 'user_1_viin_doo_test')]).unlink()
        super(MobileNotificationFirebaseCommon, self).setUp(number_partner)
        self.setup_config()
        self.channel_1.channel_last_seen_partner_ids.mobile_notification = True
        self.channel_2.channel_last_seen_partner_ids.mobile_notification = True
        # Register token
        self.list_token_register = self.list_token.copy()
        # Add function rollback
        self.addCleanup(self.rollback_database)

    def _create_new_message_channel(self, channel, author_id, number_message):
        messages = self.env['mail.message']
        for i in range(number_message):
            messages += channel.message_post(
                body='notification',
                subtype="mail.mt_comment",
                author_id=author_id,
                message_type='email',
            )
            # Need commit for user to another thread
            self.env.cr.commit()
        self.wait_thread_pool()
        return messages

    def _create_new_mail_thread(self, res_partner, author_id, partner_ids, number_message):
        messages = self.env['mail.message']
        for i in range(number_message):
            messages += res_partner.message_post(
                body='mail thread',
                subtype="mail.mt_note",
                message_type='comment',
                author_id=author_id,
                partner_ids=partner_ids,
            )
            # Need commit to user another thread
            self.env.cr.commit()
        self.wait_thread_pool()
        return messages

    def _check_request_firebase(self, url, headers, data, **kw):
        """ This method will check param of request
            If param is correct, it will return result like firebase"""
        sent_key = headers['Authorization']
        sent_key = sent_key[5:]

        self.assertEqual(url, BASE_URL, "viin_mobile_notification_firebase: wrong request url")
        self.assertEqual(sent_key, 'test_auth_key', "viin_mobile_notification_firebase: wrong request key")
        self.assertEqual(headers['Content-Type'], 'application/json', "viin_mobile_notification_firebase: wrong request Content-Type")

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
        self.wait_thread_pool()
        channel_1_messsages = self.channel_1.channel_message_ids
        channel_1_notificaitons = channel_1_messsages.mobile_notification_id
        channel_1_notificaitons.notification_detail_ids.unlink()
        channel_1_notificaitons.unlink()
        channel_1_messsages.unlink()
        partners = self.channel_1.channel_partner_ids
        self.channel_1.channel_last_seen_partner_ids.unlink()

        channel_2_messsages = self.channel_2.channel_message_ids
        channel_2_notificaitons = channel_2_messsages.mobile_notification_id
        channel_2_notificaitons.notification_detail_ids.unlink()
        channel_2_notificaitons.unlink()
        channel_2_messsages.unlink()
        self.channel_2.channel_last_seen_partner_ids.unlink()

        partners.mobile_token_ids.unlink()
        message_create_partner = self.env['mail.message'].search([('model', '=', 'res.parnter'), ('res_id', 'in', partners.ids)])
        message_create_partner.unlink()
        # Do not unlink partner of user demo
        partners[1:].unlink()
        self.channel_1.unlink()
        self.channel_2.unlink()
        
        ConfigParams = self.env['ir.config_parameter'].sudo()
        ConfigParams.set_param('mobile.notify_provider', False)
        ConfigParams.set_param('mobile.notify_auth_key', False)
        ConfigParams.set_param('mobile.notify_type', False)
        ConfigParams.set_param('mobile.notify_max_retry', 5)
        ConfigParams.set_param('mobile.base_package', False)
        self.env.cr.commit()

    def wait_thread_pool(self):
        """This method will wait all thread pool finish, then save result in database"""
        sleep(1)
        while get_count_worker_request() > 0:
            sleep(1)
        sleep(1)
        while get_count_worker_update_database() > 0:
            sleep(1)
        self.env.cr.commit()
