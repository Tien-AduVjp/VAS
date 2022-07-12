from odoo.tests import tagged, SavepointCase


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessTicket(SavepointCase):

    def test_user_who_following_task_or_project_read_ticket(self):
        user_demo = self.env.ref('base.user_demo')
        task = self.env.ref('project.project_task_11')
        task.message_subscribe(partner_ids=user_demo.partner_id.ids)
        ticket = self.env['helpdesk.ticket'].with_user(self.env.ref('base.user_admin')).create({
            'name': 'Ticket test',
            'project_id': task.project_id.id,
            'task_id': task.id
        })
        ticket.read(['name'])
        task.project_id.message_subscribe(partner_ids=user_demo.partner_id.ids)
        ticket.read(['name'])
