from odoo.addons.test_mail.tests.test_mail_followers import DuplicateNotificationTest

from . import models


def test_no_duplicate_notification_plus(self):
    """Override test_no_duplicate_notification_plus
    Because with Handle by Emails: now offers both inbox and email notifications
    """
    # Origining code

    #Simulate case of 2 users that got their partner merged
    common_partner = self.env['res.partner'].create({"name": "demo1", "email": "demo1@test.com"})
    user_1 = self.env['res.users'].create({'login': 'demo1', 'partner_id': common_partner.id, 'notification_type': 'email'})
    user_2 = self.env['res.users'].create({'login': 'demo2', 'partner_id': common_partner.id, 'notification_type': 'inbox'})

    #Trigger auto subscribe notification
    test = self.env['mail.test.track'].create({"name": "Test Track", "user_id": user_2.id})
    mail_message = self.env['mail.message'].search([
         ('res_id', '=', test.id),
         ('model', '=', 'mail.test.track'),
         ('message_type', '=', 'user_notification')
    ])
    notif = self.env['mail.notification'].search([
        ('mail_message_id', '=', mail_message.id),
        ('res_partner_id', '=', common_partner.id)
    ])

    # Origining code
    #===========================================================================
    # self.assertEqual(len(notif), 1)
    # self.assertEqual(notif.notification_type, 'email')
    #===========================================================================

    # Overriding code
    # Because with Handle by Emails: now offers both inbox and email notifications
    self.assertEqual(len(notif), 2)
    self.assertEqual(notif.mapped('notification_type'), ['email', 'inbox'])

    # Origining code
    subtype = self.env.ref('mail.mt_comment')
    res = self.env['mail.followers']._get_recipient_data(test, 'comment',  subtype.id, pids=common_partner.ids)
    partner_notif = [r for r in res if r[0] == common_partner.id]
    self.assertEqual(len(partner_notif), 1)
    self.assertEqual(partner_notif[0][5], 'email')


def post_load():
    DuplicateNotificationTest.test_no_duplicate_notification = test_no_duplicate_notification_plus
