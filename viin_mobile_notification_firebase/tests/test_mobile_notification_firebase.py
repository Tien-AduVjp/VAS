from unittest.mock import patch
import json
from odoo.tests import tagged
from odoo.addons.viin_mobile_notification_firebase.tests.common import MobileNotificationFirebaseCommon


@tagged('post_install', '-at_install', 'viin_mobile')
class TestMobileNotificationFirebase(MobileNotificationFirebaseCommon):
    def test_10_notificaiton(self):
        """ unregiser first, second, third token
            partner_0 have no token was registered, notificaiton of partner_0 have state failed
            partner_1 have a token was registered, notification of partner_1 have state success
            all notificaiton of  another partner have state success"""
        first_token = self.list_partner[0].mobile_token_ids[0].token
        second_token = self.list_partner[0].mobile_token_ids[1].token
        third_token = self.list_partner[1].mobile_token_ids[0].token
        self.list_token_register.remove(first_token)
        self.list_token_register.remove(second_token)
        self.list_token_register.remove(third_token)
        with patch('requests.post', self._check_request_firebase):
            notification = self._create_new_message_channel(self.channel_2, self.list_partner[1].id, 1)[0].mobile_notification_id
        # Check state of nofiticaion
        self.assertEqual(notification.state, 'waiting', "viin_mobile_notification_firebase: wrong update state of notification")
        for detail in notification.notification_detail_ids:
            if detail.partner_id.id == self.list_partner[0].id:
                self.assertEqual(detail.state, 'failed', "viin_mobile_notification_firebase: wrong update state of notification detail")
            else:
                self.assertEqual(detail.state, 'success', "viin_mobile_notification_firebase: wrong update state of notification detail")

        token_unlink = self.env['mobile.device.token'].search([('token', '=', first_token)])
        self.assertEqual(not token_unlink, True, "viin_mobile_notification_firebase: can't unlink token NotRegistered")
        self.check_11_channel_seen()

    def check_11_channel_seen(self):
        """ When user seen on channel, this module will send notification to cancel notification on mobile devices
            Need check param of request
            The details of notification will change state to success"""
        token_new = self._token_vals('token_new', platform='android')
        self.list_token.append(token_new['token'])
        self._create_device_token(self.user_1.partner_id, token_new)
        with patch('requests.post', self._check_request_cancel):
            self.channel_2.with_user(self.user_1).channel_seen()
        self.channel_2.flush()
        message = self.channel_2.channel_message_ids[0]
        notification = message.mobile_notification_id
        self.assertEqual(notification.state, 'success', "viin_mobile_notification_firebase: wrong update state of notification")

    def test_12_new_mail_thread(self):
        with patch('requests.post', self._check_request_firebase):
            messages = self._create_new_mail_thread(
                res_partner=self.list_partner[1],
                author_id=self.list_partner[1].id,
                partner_ids=[self.list_partner[0].id],
                number_message=3
            )
        notificaitions = messages.sudo().mobile_notification_id
        list_state = list(set(notificaitions.mapped('state')))
        self.assertEqual(len(list_state), 1, "viin_mobile_notification_firebase: wrong update state of notification")
        self.assertEqual(list_state[0], 'success', "viin_mobile_notification_firebase: wrong update state of notification")

        self.check_13_set_message_done(messages[0])
        self.check_14_mark_all_as_read(messages)
        # rollback
        notificaitions.notification_detail_ids.unlink()
        notificaitions.unlink()
        messages.unlink()
        

    def check_13_set_message_done(self, message):
        """ When user click done message, this module will send notification to cancel notification on mobile devices
            Need check param of request"""
        with patch('requests.post', self._check_request_cancel):
            message.with_user(self.user_1).set_message_done()

    def check_14_mark_all_as_read(self, messages):
        """ When user click mark all as read, this module will send notification to cancel notifications on mobile devices
            Need check param of request"""
        with patch('requests.post', self._check_request_cancel):
            messages.with_user(self.user_1).mark_all_as_read()

    def test_15_resend(self):
        """ Function resend will find and resend notificaiton has state new, waiting
            Need check param of request,
            Check state and retry count of notificaiton details"""
        # Create notificaiton success
        with patch('requests.post', self._check_request_firebase):
            notification_success = self._create_new_message_channel(self.channel_2, self.list_partner[1].id, 1)[0].mobile_notification_id
        # Create notificaiton waiting
        # unregister token of first partner
        first_token = self.list_partner[0].mobile_token_ids[0].token
        second_token = self.list_partner[0].mobile_token_ids[1].token
        self.list_token_register.remove(first_token)
        self.list_token_register.remove(second_token)
        with patch('requests.post', self._check_request_firebase):
            notification_waiting = self._create_new_message_channel(self.channel_2, self.list_partner[1].id, 1)[0].mobile_notification_id

        # Run function resend
        with patch('requests.post', self._check_request_firebase):
            self.env['mobile.notification']._resend()
            self.wait_thread_pool()
        sum_retry_count_1 = sum(notification_success.notification_detail_ids.mapped('retried_count'))
        self.assertEqual(sum_retry_count_1, 0, "viin_mobile_notification_firebase: wrong function resend, it resend notification has state success")

        notification_detail_failed = notification_waiting.notification_detail_ids.filtered(lambda r: r.state == 'failed')

        self.assertEqual(notification_waiting.state, 'waiting', "viin_mobile_notification_firebase: wrong function resend, wrong update state of notification_waiting")
        self.assertEqual(notification_detail_failed.state, 'failed', "viin_mobile_notification_firebase: wrong function resend, it wasn't resend notification has state waiting")
        self.assertEqual(notification_detail_failed.retried_count, 1, "viin_mobile_notification_firebase: wrong function resend, it wasn't resend notification has state waiting")
        self.check_16_max_retry(notification_waiting, notification_detail_failed)

    def check_16_max_retry(self, notification_waiting, notification_detail_failed):
        """ On config setting have fields max retry
            Each notification details will be resend up to max retry
            If all of it failed, notification detail will be marked as canceled"""
        notify_max_retry = int(self.env['ir.config_parameter'].sudo().get_param('mobile.notify_max_retry', 5))
        # test max retry, resend 5 time
        with patch('requests.post', self._check_request_firebase):
            for i in range(notify_max_retry):
                self.env['mobile.notification']._resend()
                self.wait_thread_pool()

        self.assertEqual(notification_waiting.state, 'partially_success', "viin_mobile_notification_firebase: wrong function resend, wrong update state of notification_waiting")
        self.assertEqual(notification_detail_failed.state, 'cancelled', "viin_mobile_notification_firebase: wrong function resend, it wasn't resend notification has state waiting")
        self.assertEqual(notification_detail_failed.retried_count, 5, "viin_mobile_notification_firebase: wrong function resend, it wasn't resend notification has state waiting")

    def test_17_resend_add_token_again(self):
        """ Fist time, user_1 have no token was registered, create notification_waiting
            Before cron call _resend, registered token again
            After cron run, notification_waiting will have state success"""
        first_token = self.list_partner[0].mobile_token_ids[0].token
        second_token = self.list_partner[0].mobile_token_ids[1].token
        self.list_token_register.remove(first_token)
        self.list_token_register.remove(second_token)
        with patch('requests.post', self._check_request_firebase):
            notification_waiting = self._create_new_message_channel(self.channel_2, self.list_partner[1].id, 1)[0].mobile_notification_id
        first_token = self._token_vals(first_token, platform='ios')
        self._create_device_token(self.user_1.partner_id, first_token)
        self.env.cr.commit()
        self.list_token_register.append(first_token['token'])
        # Run function resend
        with patch('requests.post', self._check_request_firebase):
            self.env['mobile.notification']._resend()
            self.wait_thread_pool()
        self.assertEqual(notification_waiting.state, 'success', "viin_mobile_notification_firebase: wrong function resend, wrong update state of notification_waiting")

    def _check_request_cancel(self, url, headers, data, **kw):
        """This method will check param of request"""
        response = self._check_request_firebase(url, headers, data)
        data = json.loads(data)
        registration_ids = data['registration_ids']
        user_1_tokens = self.user_1.partner_id.mobile_token_ids
        for token in user_1_tokens:
            self.assertEqual(token.token in registration_ids, True, "viin_mobile_notification_firebase: wrong token when send canel notification")
        return response
