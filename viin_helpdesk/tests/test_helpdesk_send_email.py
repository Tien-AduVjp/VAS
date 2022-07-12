from odoo.tests import tagged, SavepointCase


@tagged('post_install', '-at_install')
class TestHelpdeskSendEmail(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskSendEmail, cls).setUpClass()
        cls.env.company.default_helpdesk_team_id.stage_ids = [(4, cls.env.ref('viin_helpdesk.helpdesk_stage_resolved').id)]

    def test_send_email_01(self):
        """ Create ticket uncheck send noti email => do not send email """
        ticket = self.env['helpdesk.ticket'].with_user(self.env.ref('base.user_admin')).create({
            'name': 'Ticket Test 01',
            'team_id': self.env.company.default_helpdesk_team_id.id,
            'partner_id': self.env.ref('base.partner_demo_portal').id
        })
        message = self.env['mail.message'].search([
            ('model', '=', 'helpdesk.ticket'),
            ('res_id', '=', ticket.id),
            ('notification_ids', '!=', False)
        ])
        self.assertFalse(message)

    def test_send_email_02(self):
        """ Ticket check send noti email, stage include template, change stage => send email """
        user = self.env.ref('base.user_admin')
        portal_user = self.env.ref('base.partner_demo_portal')
        ticket = self.env['helpdesk.ticket'].with_user(user).create({
            'name': 'Ticket Test 03',
            'team_id': self.env.company.default_helpdesk_team_id.id,
            'partner_id': portal_user.id,
            'stage_id': self.env.ref('viin_helpdesk.helpdesk_stage_new').id,
            'send_notification_email': True
        })
        # Since v14 the tracking mechanism has changed, when a record is created it will be marked as discard tracking
        # in precommit data. Because in this test case the creation and editing are both in the same transaction so tracking
        # values when writing record is impossible. To solve this problem we have to clean the precommit data before
        # writing for the tracking values to take effect.
        self.cr.precommit.data.clear()
        ticket.write({'stage_id': self.env.ref('viin_helpdesk.helpdesk_stage_resolved').id})
        # Force tracking values
        self.cr.precommit.run()
        message = self.env['mail.message'].search([
            ('model', '=', 'helpdesk.ticket'),
            ('res_id', '=', ticket.id),
            ('body', 'ilike', 'has been processed successfully'),
            ('notification_ids', '!=', False),
            ('partner_ids', 'in', [user.id, portal_user.id])
        ])
        self.assertTrue(message)

    def test_send_email_03(self):
        """ Create ticket check send noti email, rating status = stage, stage include template, change stage => send email """
        user = self.env.ref('base.user_admin')
        portal_user = self.env.ref('base.partner_demo_portal')
        ticket = self.env['helpdesk.ticket'].with_user(user).create({
            'name': 'Ticket Test',
            'team_id': self.env.company.default_helpdesk_team_id.id,
            'partner_id': self.env.ref('base.partner_demo_portal').id,
            'send_notification_email': True,
            'rating_status': 'stage'
        })
        self.cr.precommit.data.clear()
        ticket.write({'stage_id': self.env.ref('viin_helpdesk.helpdesk_stage_resolved').id})
        self.cr.precommit.run()
        message = self.env['mail.message'].search([
            ('model', '=', 'helpdesk.ticket'),
            ('res_id', '=', ticket.id),
            ('subject', 'ilike', 'Satisfaction Survey'),
            ('notification_ids', '!=', False),
            ('partner_ids', 'in', [user.id, portal_user.id])
        ])
        self.assertTrue(message)
