import json

from odoo.tests import tagged, common, get_db_name

from .common import MobileNotificationCommon


@tagged('post_install', '-at_install', 'viin_mobile')
class TestMobileNotificationController(MobileNotificationCommon, common.HttpCase):

    def setUp(self, number_partner=4):
        super(TestMobileNotificationController, self).setUp(number_partner)
        self.base_url = self.user_1.get_base_url()
        self.headers = {'Content-Type': 'application/json'}
        self.db = get_db_name()
        data_login = {
            "jsonrpc": "2.0",
            "params": {
                "db": self.db,
                "login": self.user_1.login,
                "password": 'demo',
                }
            }
        self.opener.post(self.base_url + '/web/session/authenticate', headers=self.headers, data=json.dumps(data_login))

    def test_00_add_token(self):
        # add new token success
        new_token = self._token_vals('new_token')
        data_token = {
            "jsonrpc": "2.0",
            "params": {
                "token": new_token['token'],
                "platform": new_token['platform'],
                "package_name": new_token['package_name'],
                }
            }
        response_success = self.opener.post(self.base_url + '/mobile/notifications/add/token', headers=self.headers, data=json.dumps(data_token))
        self.assertEqual(response_success.status_code, 200, "viin_mobile_notification: can't connect service")
        result_success = response_success.json()['result']
        self.assertEqual(result_success['message'], "Add success", "viin_mobile_notification: add token error")

        # If token already exists, api will return message Token already exists
        response_fail = self.opener.post(self.base_url + '/mobile/notifications/add/token', headers=self.headers, data=json.dumps(data_token))
        result_fail = response_fail.json()['result']
        self.assertEqual(result_fail['message'], "Token already exists", "viin_mobile_notification: add token error")

        # Change token for new partner
        token_test = self.list_token_obj[3]
        data_token_2 = {
            "jsonrpc": "2.0",
            "params": {
                "token": token_test['token'],
                "platform": token_test['platform'],
                "package_name": token_test['package_name'],
                }
            }
        response_success_1 = self.opener.post(self.base_url + '/mobile/notifications/add/token', headers=self.headers, data=json.dumps(data_token_2))
        self.assertEqual(response_success_1.status_code, 200, "viin_mobile_notification: can't connect service")
        result_success_1 = response_success_1.json()['result']
        self.assertEqual(result_success_1['message'], "Add success", "viin_mobile_notification: add token error")

    def test_01_delete_token(self):
        token_1 = self.list_token_obj[0]
        data_token = {
            "jsonrpc": "2.0",
            "params": {
                "token": token_1['token'],
                }
            }
        response_success = self.opener.post(self.base_url + '/mobile/notifications/logout', headers=self.headers, data=json.dumps(data_token))
        self.assertEqual(response_success.status_code, 200, "viin_mobile_notification: can't connect service")
        result_success = response_success.json()['result']
        self.assertEqual(result_success['message'], "Delete success", "viin_mobile_notification: delete token error")

        response_fail = self.opener.post(self.base_url + '/mobile/notifications/logout', headers=self.headers, data=json.dumps(data_token))
        self.assertEqual(response_fail.status_code, 200, "viin_mobile_notification: can't connect service")
        result_fail = response_fail.json()['result']
        self.assertEqual(result_fail['message'], "Token does not exist", "viin_mobile_notification: delete token error")

    def test_02_mobile_get_info_notification(self):
        """ Fisrt time call this test will return:
            unread_counters = 4
            mail_inbox_counters = 1
            mobile_inbox_date = now
            mobile_channel_seens:{}"""
        # Need unlink for counter
        self.env['mail.notification'].search([("res_partner_id.id", "=", self.user_1.partner_id.id)]).unlink()
        self.set_up_mess_for_channel(
            channel=self.channel_1,
            number_message=4,
            author=self.list_partner[1],
            partner_1=self.list_partner[0],
            partner_2=self.list_partner[2]
        )
        # need leave channel general for counter message
        self.MailChannelPartner.search([('channel_id', '=', 1)]).unlink()
        message_notification = self.set_up_notify_for_mail_thread(
            number_message=1,
            author=self.list_partner[1],
            partner_1=self.list_partner[0],
            partner_2=self.list_partner[2])
        data_notification_info = {
            "jsonrpc": "2.0",
            "params": {
                "mobile_channel_seens": {},
                "mobile_inbox_date": "2021-06-11 06:11:48",
                }
            }
        response = self.opener.post(self.base_url + '/mobile/notifications/notification_info', headers=self.headers, data=json.dumps(data_notification_info))
        self.assertEqual(response.status_code, 200, "viin_mobile_notification: can't connect service")
        result = response.json()['result']
        self.assertEqual(result['unread_counters'], 4, "viin_mobile_notification: mobile_get_info_notification error unread_counters")
        self.assertEqual(result['mail_inbox_counters'], 1, "viin_mobile_notification: mobile_get_info_notification error mail_inbox_counters")
        self.assertEqual(len(result['notify_groups']), 0, "viin_mobile_notification: mobile_get_info_notification error notify_groups")

        # Save result for next call
        data_notification_info = {
            "jsonrpc": "2.0",
            "params": {
                "mobile_channel_seens": result['mobile_channel_seens'],
                "mobile_inbox_date": result['mobile_inbox_date'],
                }
            }
        """ User_1 read message on channel_1
            Next call will return:
            unread_counters = 0
            mail_inbox_counters = 1
            mobile_inbox_date = now
            mobile_channel_seens:{"channel_1.id": last_message.id}"""
        self.channel_1.with_user(self.user_1).channel_seen()
        self.channel_1.flush()
        response = self.opener.post(self.base_url + '/mobile/notifications/notification_info', headers=self.headers, data=json.dumps(data_notification_info))
        result = response.json()['result']
        self.assertEqual(result['unread_counters'], 0, "viin_mobile_notification: mobile_get_info_notification error unread_counters")
        self.assertEqual(result['mail_inbox_counters'], 1, "viin_mobile_notification: mobile_get_info_notification error mail_inbox_counters")
        self.assertEqual(len(result['notify_groups']), 0, "viin_mobile_notification: mobile_get_info_notification error notify_groups")

        # Save result for next call
        data_notification_info = {
            "jsonrpc": "2.0",
            "params": {
                "mobile_channel_seens": result['mobile_channel_seens'],
                "mobile_inbox_date": result['mobile_inbox_date'],
                }
            }
        """ user_1 set_message_done message_notification
            Next call will return:
            unread_counters = 0
            mail_inbox_counters = 0
            mobile_inbox_date = now
            mobile_channel_seens:{}"""
        message_notification.with_user(self.user_1).set_message_done()
        message_notification.flush()
        response = self.opener.post(self.base_url + '/mobile/notifications/notification_info', headers=self.headers, data=json.dumps(data_notification_info))
        self.assertEqual(response.status_code, 200, "viin_mobile_notification: can't connect service")
        result = response.json()['result']
        self.assertEqual(result['unread_counters'], 0, "viin_mobile_notification: mobile_get_info_notification error unread_counters")
        self.assertEqual(result['mail_inbox_counters'], 0, "viin_mobile_notification: mobile_get_info_notification error mail_inbox_counters")
        self.assertEqual(len(result['notify_groups']), 0, "viin_mobile_notification: mobile_get_info_notification error notify_groups")
