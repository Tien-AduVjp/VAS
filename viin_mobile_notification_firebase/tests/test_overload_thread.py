from unittest.mock import patch
from odoo.tests import tagged
from odoo.addons.viin_mobile_notification_firebase.tests.common import MobileNotificationFirebaseCommon


@tagged('-at_install',  '-standard', 'viin_mobile_overload')
class TestNotificationOverload(MobileNotificationFirebaseCommon):
    def setUp(self, number_partner=100):
        super(TestNotificationOverload, self).setUp(number_partner)

    def test_00_overload_thread(self):
        # Clean data before start test
        old_messsages = self.channel_1.channel_message_ids
        old_notificaitons = old_messsages.mobile_notification_id
        old_notificaitons.notification_detail_ids.unlink()
        old_notificaitons.unlink()
        old_messsages.unlink()
        self.env.cr.commit()
        with patch('requests.post', self._check_request_firebase):
            self._create_new_message_channel(self.channel_1, self.list_partner[0].id, 100)
        # Check state of nofiticaion
        messages = self.channel_1.channel_message_ids
        notifications = messages.mobile_notification_id
        list_state = notifications.mapped('state')
        list_state = list(set(list_state))
        self.assertEqual(len(list_state), 1, "viin_mobile_notification_firebase: wrong update state of notification")
        self.assertEqual(list_state[0], 'success', "viin_mobile_notification_firebase: wrong update state of notification")
