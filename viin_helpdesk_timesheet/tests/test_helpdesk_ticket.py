from odoo.tests import tagged

from odoo.addons.viin_helpdesk.tests.test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external')
class TestHelpdeskTicket(TestHelpdeskCommon):
    def test_set_project_id_to_false(self):
        project = self.env.ref('project.project_project_1')
        project_task = self.env.ref('project.project_task_7')
        ticket = self.ticket_user
        ticket.write({
            'project_id': project.id,
            'task_id': project_task.id,
        })
        self.assertIn(ticket, project_task.ticket_ids)
        ticket.write({
            'project_id': False,
        })
        self.assertNotIn(ticket.id, project_task.ticket_ids.ids)
