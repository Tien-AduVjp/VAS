from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.viin_helpdesk.tests.test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external')
class TestTask2Ticket(TestHelpdeskCommon):

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_task2ticket(self, mock_send_mail):
        mock_send_mail.return_value = True

        team_general = self.team_general
        self.ticket_type = self.env.ref('viin_helpdesk.helpdesk_ticket_type_question')
        task = self.env.ref('project.project_task_1')

        # Check data
        self.assertEqual(True, task.active, 'Task is not active')
        self.assertEqual(0, task.tickets_count, 'Task has been links with ticket')

        # Test: lead2ticket
        task2ticket = self.env['task2ticket.wizard'].with_context(active_ids=[task.id]).create({
            'ticket_type_id': self.ref('viin_helpdesk.helpdesk_ticket_type_question'),
            'team_id': team_general.id,
            })
        task2ticket.action_create_ticket()

        self.assertEqual(False, task.active, 'Task is active')
        task.invalidate_cache()  # to recompute tickets_count's value
        self.assertEqual(1, task.tickets_count, 'Task has not been links with ticket')

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_task2ticket_for_yourself(self, mock_send_mail):
        mock_send_mail.return_value = True

        team_general = self.team_general
        task = self.env.ref('project.project_task_2')
        task.project_id.user_id = self.user_member_user.id
        # Check data
        self.assertEqual(True, task.active, 'Task is not active')
        self.assertEqual(0, task.tickets_count, 'Task has been links with ticket')

        # Test: lead2ticket
        self.user_member_user.write({'groups_id': [(4, self.ref('project.group_project_user'))]})
        task2ticket = self.env['task2ticket.wizard'] \
                        .with_context(active_ids=[task.id]) \
                        .with_user(self.user_member_user).create({
                            'ticket_type_id': self.ref('viin_helpdesk.helpdesk_ticket_type_question'),
                            'team_id': team_general.id,
                            'assign_to_me': True,
                            })
        task2ticket.action_create_ticket()

        self.assertEqual(False, task.active, 'Task is active')
        task.invalidate_cache()  # to recompute tickets_count's value
        self.assertEqual(1, task.tickets_count, 'Task has not been links with ticket')
        self.assertEqual(self.user_member_user, task.ticket_ids.user_id, 'Test not ok')
