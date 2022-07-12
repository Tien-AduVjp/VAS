from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.viin_helpdesk.tests.test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external')
class TestTask2Ticket(TestHelpdeskCommon):

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_ticket2task(self, mock_send_mail):
        mock_send_mail.return_value = True

        task = self.env.ref('project.project_task_1')
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'ticket_demo',
            'project_id': task.project_id.id
            })

        # Check data
        self.assertEqual(True, ticket.active, 'Task is not active')

        # Test: lead2ticket
        ticket2task = self.env['ticket2task.wizard'].with_context(active_ids=[ticket.id]).create({
            'project_id': task.project_id.id,
            })
        ticket2task.action_create_task()

        self.assertEqual(False, ticket.active, 'Task is active')
        ticket.invalidate_cache()  # to recompute tickets_count's value
