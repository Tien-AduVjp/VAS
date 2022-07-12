from odoo.exceptions import AccessError, AccessDenied, UserError
from odoo.tools import mute_logger
from odoo.tests import tagged
from odoo import SUPERUSER_ID

from .test_helpdesk_common import TestHelpdeskCommon


@tagged('post_install', '-at_install', 'external', 'access_rights')
class TestAccessRightsBase(TestHelpdeskCommon):
    
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_public_user_ticket_access_rights(self):
        team_general = self.team_general
        
        # Test: team visible
        team_general.write({'privacy_visibility': 'followers'})
        team_general.flush(['privacy_visibility'])
        self.assertRaises(AccessError, team_general.with_user(self.user_public).read, ['team_leader_id'])
        
        team_general.write({'privacy_visibility': 'employees'})
        team_general.flush(['privacy_visibility'])
        self.assertRaises(AccessError, team_general.with_user(self.user_public).read, ['team_leader_id'])
        
        team_general.write({'privacy_visibility': 'portal'})
        team_general.flush(['privacy_visibility'])
        self.assertRaises(AccessError, team_general.with_user(self.user_public).read, ['team_leader_id'])
        
        # Test: ticket visible
        # read, write, delete another ticket
        ticket_public = self.ticket_public
        another_ticket = self.ticket_portal.with_user(self.user_public)
        with self.assertRaises(AccessError):
            another_ticket.read(['name'])
            another_ticket.name = 'Ticket Public Test'
            another_ticket.unlink()
        # read, write, delete own ticket
        ticket_public.read(['name'])
        ticket_public.name = 'Ticket Public Test'
        ticket_public.unlink()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_portal_user_ticket_access_rights(self):
        team_general = self.team_general
        ticket_public = self.ticket_public
        ticket_portal = self.ticket_portal

        # Test: team visible
        team_general.write({'privacy_visibility': 'followers'})
        team_general.flush(['privacy_visibility'])
        self.assertRaises(AccessError, team_general.with_user(self.user_portal).read, ['team_leader_id'])
        
        team_general.write({'privacy_visibility': 'employees'})
        team_general.flush(['privacy_visibility'])
        self.assertRaises(AccessError, team_general.with_user(self.user_portal).read, ['team_leader_id'])
        
        team_general.write({'privacy_visibility': 'portal'})
        team_general.flush(['privacy_visibility'])
        self.assertEqual(team_general.id, team_general.with_user(self.user_portal).read(['id'])[0]['id'], 'Test read team with portal user not ok')
        
        # Test: ticket visible
        self.assertRaises(AccessError, ticket_public.with_user(self.user_portal).read, ['id'])
        self.assertEqual(ticket_portal.id, ticket_portal.with_user(self.user_portal).read(['id'])[0]['id'], 'Test read ticket with portal user not ok')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_employee_user_ticket_access_rights(self):
        team_general = self.team_general
        ticket_public = self.ticket_public
        ticket_portal = self.ticket_portal
        ticket_employee = self.ticket_employee

        # Test: team visible
        # Test: employee have assigned ticket
        team_general.write({'privacy_visibility': 'followers'})
        team_general.flush(['privacy_visibility'])
        self.assertEqual(team_general.id, team_general.with_user(self.user_employee_user).read(['id'])[0]['id'], 'Test read team with employee user not ok')
        # Test: write
        self.assertRaises(AccessError, team_general.with_user(self.user_employee_user).write, {'name': 'General'})
        
        # Test: employee no have assigned ticket
        ticket_employee.write({'team_id': False})
        ticket_employee.flush(['team_id'])
        self.assertRaises(AccessError, team_general.with_user(self.user_employee_user).read, ['team_leader_id'])

        # Test: employee following this team
        team_general.message_subscribe(self.user_employee_user.partner_id.ids)
        team_general.flush(['message_partner_ids'])
        self.assertEqual(team_general.id, team_general.with_user(self.user_employee_user).read(['id'])[0]['id'], 'Test read team with employee user not ok')
        self.assertRaises(AccessError, team_general.with_user(self.user_employee_user).write, {'name': 'General'})
        
        team_general.write({
            'privacy_visibility': 'employees',
            'message_partner_ids': [],
            })
        team_general.flush(['privacy_visibility', 'message_partner_ids'])
        self.assertEqual(team_general.id, team_general.with_user(self.user_employee_user).read(['id'])[0]['id'], 'Test read team with employee user not ok')
        self.assertRaises(AccessError, team_general.with_user(self.user_employee_user).write, {'name': 'General'})
        
        team_general.write({'privacy_visibility': 'portal'})
        team_general.flush(['privacy_visibility'])
        self.assertEqual(team_general.id, team_general.with_user(self.user_employee_user).read(['id'])[0]['id'], 'Test read team with employee user not ok')
        self.assertRaises(AccessError, team_general.with_user(self.user_employee_user).write, {'name': 'General'})
        
        # Test: ticket visible
        self.assertRaises(AccessError, ticket_public.with_user(self.user_employee_user).read, ['id'])
        self.assertRaises(AccessError, ticket_portal.with_user(self.user_employee_user).read, ['id'])
        self.assertEqual(ticket_employee.id, ticket_employee.with_user(self.user_employee_user).read(['id'])[0]['id'], 'Test read ticket with employee user not ok')
        
        # Test: employee assigned
        ticket_portal.write({'user_id': self.user_employee_user.id})
        ticket_portal.flush(['user_id'])
        self.assertEqual(ticket_portal.id, ticket_portal.with_user(self.user_employee_user).read(['id'])[0]['id'], 'Test read ticket with employee user not ok')
        
        # Test: employee belong team and following this ticket
        ticket_public.message_subscribe(self.user_employee_user.partner_id.ids)
        ticket_public.flush(['message_partner_ids'])
        self.assertEqual(ticket_public.id, ticket_public.with_user(self.user_employee_user).read(['id'])[0]['id'], 'Test read ticket with employee user not ok')
        
        # Test: unlink (created)
        ticket_employee.with_user(SUPERUSER_ID).write({'team_id': self.team_general.id})
        ticket_employee.flush(['team_id'])
        
        self.assertRaises(AccessDenied, ticket_public.with_user(self.user_employee_user).unlink)
        
        ticket_employee.with_user(SUPERUSER_ID).write({'stage_id': self.assigned_stage.id})
        ticket_employee.flush(['stage_id'])
        
        self.assertRaises(AccessDenied, ticket_employee.with_user(self.user_employee_user).write, {'name': 'Ticket 1'})
        self.assertRaises(AccessDenied, ticket_employee.with_user(self.user_employee_user).unlink)
        
        ticket_employee.with_user(SUPERUSER_ID).write({'stage_id': self.new_stage.id})
        ticket_employee.flush(['stage_id'])
        self.assertEqual(True, ticket_employee.with_user(self.user_employee_user).write({'name': 'Ticket 1'}), 'Test write ticket with employee user not ok')
        self.assertEqual(True, ticket_employee.with_user(self.user_employee_user).unlink(), 'Test unlink ticket with employee user not ok')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_user_group_ticket_access_rights(self):
        team_general = self.team_general
        ticket_public = self.ticket_public
        ticket_portal = self.ticket_portal
        ticket_employee = self.ticket_employee
        ticket_leader = self.ticket_leader
        user_member_user = self.user_member_user
        user_helpdesk_user = self.user_helpdesk_user
        user_leader_user = self.user_leader_user

        # Test: team visible
        # Test: user_member_user have assigned ticket
        team_general.write({
            'privacy_visibility': 'followers',
            })
        team_general.flush(['privacy_visibility', 'team_member_ids'])
        self.assertEqual(team_general.id, team_general.with_user(user_member_user).read(['id'])[0]['id'], 'Test read team with user not ok')
        # Test user_member_user: write
        self.assertRaises(AccessError, team_general.with_user(user_member_user).write, {'name': 'General'})
        
        # Test user_member_user: read ticket
        self.assertEqual(ticket_public.id, ticket_public.with_user(user_member_user).read(['id'])[0]['id'], 'Test read ticket with user not ok')
        self.assertEqual(ticket_portal.id, ticket_portal.with_user(user_member_user).read(['id'])[0]['id'], 'Test read ticket with user not ok')
        self.assertEqual(ticket_employee.id, ticket_employee.with_user(user_member_user).read(['id'])[0]['id'], 'Test read ticket with user not ok')
        
        # Test user_member_user: write ticket
        tickets = (ticket_portal | ticket_employee)
        tickets.with_user(SUPERUSER_ID).write({'user_id': False})
        tickets.flush(['user_id'])
        
        self.assertRaises(AccessDenied, ticket_portal.with_user(user_member_user).write, {'name': 'ticket public'})
        self.assertRaises(AccessDenied, ticket_portal.with_user(user_member_user).write, {'name': 'ticket portal'})
        self.assertRaises(AccessDenied, ticket_employee.with_user(user_member_user).write, {'name': 'ticket employee'})
        
        # Test: employee assigned
        ticket_portal.write({'user_id': user_member_user.id})
        ticket_portal.flush(['user_id'])
        # Test read ticket
        self.assertEqual(ticket_portal.id, ticket_portal.with_user(user_member_user).read(['id'])[0]['id'], 'Test read ticket with user not ok')
        # Test user_helpdesk_user: write ticket
        team_general.write({
            'team_member_ids': [(4, user_helpdesk_user.id)]
            })
        team_general.flush(['team_member_ids'])
        ticket_portal.write({'user_id': user_helpdesk_user.id})
        ticket_portal.flush(['user_id'])
        self.assertEqual(True, ticket_portal.with_user(user_helpdesk_user).write({'name': 'ticket portal'}), 'Test write ticket with user not ok')
        # Test unlink ticket
        self.assertRaises(AccessError, ticket_portal.with_user(user_helpdesk_user).unlink)
        
        # Test write team: user is belong helodesk user group and is not leader
        self.assertRaises(AccessError, team_general.with_user(user_helpdesk_user).write, {'name': 'General 1'})
        
        # Test write team: user is belong helodesk user group and not leader
        self.assertEqual(True, team_general.with_user(user_leader_user).write({'name': 'General 1'}), 'Test write team with user not ok')
        
        # Test user_leader_user: unlink (created)
        self.assertRaises(AccessError, ticket_public.with_user(user_leader_user).unlink)
        self.assertEqual(True, ticket_leader.with_user(user_leader_user).unlink(), 'Test unlink ticket with user not ok')

    def test_leader_access_team(self):
        # Team leader allow to read, write team
        self.team_general.team_leader_id = self.user_leader_user.id
        self.team_general.with_user(self.user_leader_user).name = 'General 2'

    def test_public_user_access_stage(self):
        with self.assertRaises(AccessError):
            self.env['helpdesk.stage'].create({
                'name': 'Stage Test'
            })
            stage = self.empty_stage.with_user(self.user_public)
            stage.read(['name'])
            stage.name = 'Stage Test'
            stage.unlink()

    def test_portal_user_access_stage(self):
        stage = self.empty_stage.with_user(self.user_portal)
        stage.read(['name'])
        with self.assertRaises(AccessError):
            self.env['helpdesk.stage'].with_user(self.user_portal).create({
                'name': 'Stage Test'
            })
            stage.name = 'Stage Test'
            stage.unlink()

    def test_member_follower_ticket_access_stage(self):
        # Member User follow ticket with team using this stage => allow to read, write
        self.new_stage.team_ids.ticket_ids[:1].user_id = self.user_member_user.id
        stage = self.new_stage.with_user(self.user_member_user)
        stage.read(['name'])
        stage.name = 'Stage Test'

    def test_portal_user_access_tag(self):
        tag = self.tag.with_user(self.user_portal)
        tag.read(['name'])
        with self.assertRaises(AccessError):
            self.env['helpdesk.tag'].with_user(self.user_portal).create({'name': 'Tag test 2'})
            tag.name = 'Tag test 3'
            tag.unlink()

    def test_manager_user_access_tag(self):
        tag = self.tag.with_user(self.user_helpdesk_manager)
        tag.read(['name'])
        self.env['helpdesk.tag'].with_user(self.user_helpdesk_manager).create({'name': 'Tag test 2'})
        tag.name = 'Tag test 3'
        tag.unlink()

    def test_user_internal_access_sla(self):
        sla_test = self.env['helpdesk.sla'].create({
            'team_id': self.team_general.id,
            'name': 'SLA test',
            'stage_id': self.new_stage.id
        })
        sla = sla_test.with_user(self.user_employee_user)
        sla.read(['name'])
        with self.assertRaises(AccessError):
            sla.name = 'SLA Test 2'
            sla.unlink()

    def test_manager_access_sla(self):
        sla_test = self.env['helpdesk.sla'].with_user(self.user_helpdesk_manager).create({
            'team_id': self.team_general.id,
            'name': 'SLA test',
            'stage_id': self.new_stage.id
        })
        sla_test.read(['name'])
        sla_test.name = 'SLA test 2'
        sla_test.unlink()
