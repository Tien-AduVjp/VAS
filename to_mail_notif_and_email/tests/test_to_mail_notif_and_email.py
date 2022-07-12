from unittest.mock import patch
from odoo.tests.common import tagged, SavepointCase


@tagged('post_install', '-at_install')
class TestToMailNotifAndEmail(SavepointCase):

    def setUp(self):
        super(TestToMailNotifAndEmail, self).setUp()

        self.user_demo = self.env.ref('base.user_demo')
        self.user_admin = self.env.ref('base.user_admin')
        self.channel_1 = self.env['mail.channel'].create({
            'name': 'general',
            'public': 'public'
        })
        self.user_admin.notification_type = 'email'

    @patch('odoo.addons.mail.models.mail_thread.MailThread._notify_record_by_inbox')
    def test_notify_record_by_notify_force_from_email(self, _notify_record_by_inbox):
        self.channel_1.with_user(self.user_demo).message_post(body='hello', partner_ids=self.user_admin.partner_id.ids)
        _notify_record_by_inbox.assert_called()

        recipients_data_arg = _notify_record_by_inbox.call_args[0][1]

        for p in recipients_data_arg['partners']:
            self.assertTrue(p['notif'] == 'inbox')
