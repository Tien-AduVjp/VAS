from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError

from .test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install')
class TestHelpdesk(TestHelpdeskCommon):

    def test_unlink_stage(self):
        # Unlink stage which is already in use on any team
        with self.assertRaises(UserError):
            self.new_stage.unlink()

    def test_unlink_team(self):
        # Unlink team when it already has a ticket
        with self.assertRaises(UserError):
            self.team_general.unlink()

    def test_add_same_final_stage_in_team(self):
        self.new_stage.is_final_stage = True
        self.assigned_stage.is_final_stage = True
        with self.assertRaises(ValidationError):
            self.team_general.stage_ids = [(6, 0, [self.new_stage.id, self.assigned_stage.id])]

    def test_analysis_ticket(self):
        # Test assign_duration = (create_date - assign_date)(hours)
        self.assigned_stage.is_final_stage = True
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Ticket Test',
            'team_id': self.team_general.id
        })
        self.env.cr.execute("""UPDATE helpdesk_ticket SET create_date='%s' WHERE id=%s""" % ('2021-09-15 03:30:30', ticket.id))
        ticket.invalidate_cache()
        ticket.user_id = self.user_member_user.id
        delta = ticket.assign_date - ticket.create_date
        duration = (delta.days * 86400 + delta.seconds) / 60 / 60
        self.assertEqual(ticket.assign_duration, duration)

        # Test resolved duration
        ticket.stage_id = self.assigned_stage.id
        delta = ticket.end_date - ticket.assign_date
        duration = (delta.days * 86400 + delta.seconds) / 60 / 60
        self.assertEqual(ticket.resolved_duration, duration)

    def test_random_assign_exclude_team_leader(self):
        self.team_general.write({
            'assign_type': 'random',
            'team_member_ids': [(6, 0, [self.user_leader_user.id])]
        })
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Ticket random assign exclude leader',
            'team_id': self.team_general.id
        })
        # Expected result: no user
        self.assertFalse(ticket.user_id)

    def test_balanced_assignation(self):
        self.team_general.write({
            'assign_type': 'balanced',
            'team_member_ids': [(6, 0, [self.user_leader_user.id, self.user_employee_user.id, self.user_helpdesk_user.id])]
        })
        self.env['helpdesk.ticket'].create([{
            'name': 'Test Ticket Balanced Assignation 1',
            'user_id': self.user_leader_user.id,
            'team_id': self.team_general.id
        }, {
            'name': 'Test Ticket Balanced Assignation 2',
            'user_id': self.user_leader_user.id,
            'team_id': self.team_general.id
        }, {
            'name': 'Test Ticket Balanced Assignation 3',
            'user_id': self.user_employee_user.id,
            'team_id': self.team_general.id
        }])
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Test Ticket Balanced Assignation',
            'team_id': self.team_general.id
        })
        # Expected result: assign to the member in charge of the fewest tickets
        self.assertEqual(ticket.user_id, self.user_helpdesk_user)

    def test_random_assignation(self):
        self.team_general.write({
            'assign_type': 'random',
            'team_member_ids': [(6, 0, [self.user_leader_user.id, self.user_employee_user.id, self.user_helpdesk_user.id])],
            'team_leader_excluded': False
        })
        member_ids = self.team_general.team_member_ids.sorted('id')
        self.env['helpdesk.ticket'].create([{
            'name': 'Test Ticket Balanced Assignation 1',
            'user_id': member_ids[0].id,
            'team_id': self.team_general.id
        }, {
            'name': 'Test Ticket Balanced Assignation 2',
            'user_id': member_ids[1].id,
            'team_id': self.team_general.id
        }, {
            'name': 'Test Ticket Balanced Assignation 3',
            'user_id': member_ids[2].id,
            'team_id': self.team_general.id
        }])
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Test Ticket Balanced Assignation',
            'team_id': self.team_general.id
        })
        # Expected result: assign to the next member in the member list from the last assigned member
        self.assertEqual(ticket.user_id, member_ids[0])
