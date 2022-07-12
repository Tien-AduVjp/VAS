from odoo.tests import tagged

from odoo.addons.viin_helpdesk.tests.test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install')
class TestTicketTimesheet(TestHelpdeskCommon):

    def test_ticket_timesheet(self):
        """ Test that when timesheets on the ticket which linked to project task, this also timesheets on that project task"""
        ticket = self.ticket_user
        project = self.env.ref('project.project_project_1')
        project_task = self.env.ref('project.project_task_7')
        self.user_member_user.action_create_employee()
        self.user_member_user.groups_id = [(4, self.env.ref('hr_timesheet.group_hr_timesheet_user').id)]
        ticket.write({
            'project_id': project.id,
            'task_id': project_task.id,
            'timesheet_ids': [(0, 0, {
                'name': 'Time sheet line 01',
                'employee_id': self.user_member_user.employee_id.id,
                'project_id': project.id,
                'task_id': project_task.id
            })]
        })
        self.assertIn(ticket.timesheet_ids, project_task.timesheet_ids)
