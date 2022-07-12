from odoo.tests import tagged
from odoo.exceptions import AccessError

from .common import MobileNotificationCommon


@tagged('post_install', '-at_install', 'viin_mobile')
class TestMobileNotificationSecurity(MobileNotificationCommon):

    def setUp(self, number_partner=4):
        super(TestMobileNotificationSecurity, self).setUp(number_partner)
        self.set_up_mess_for_channel(
            self.channel_1,
            1,
            self.list_partner[0],
            self.list_partner[1], self.list_partner[2]
        )
        self.user_2 = self.env['res.users'].create(self._user_vals('user_2_viin_doo_test', self.list_partner[0]))
        group_admin_setting = self.env.ref('base.group_erp_manager').id
        self.user_1.write({
            'groups_id': [(6, 0, [group_admin_setting])],
        })

    def test_00_mobile_notification_security(self):
        """Only user has permission setting can read mobile notification"""
        notify_new = self.channel_1.channel_message_ids[0].mobile_notification_id
        notify_new.with_user(self.user_1).read(['id'])
        self.assertRaises(AccessError, notify_new.with_user(self.user_2).read, ['id'])
