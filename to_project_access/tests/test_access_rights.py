from odoo.tests import tagged
from odoo.exceptions import AccessError
from odoo.tools import mute_logger

from .test_project_base import TestProjectBase


@tagged('access_rights')
class TestPortalProjectBase(TestProjectBase):

    def setUp(self):
        super(TestPortalProjectBase, self).setUp()

        user_group_employee = self.env.ref('base.group_user')
        user_group_project_user = self.env.ref('project.group_project_user')

        self.user_noone = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'Noemie NoOne',
            'login': 'noemie',
            'email': 'n.n@example.viindoo.com',
            'signature': '--\nNoemie',
            'notification_type': 'email',
            'groups_id': [(6, 0, [])]})

        self.user_follower = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'Jack Follow',
            'login': 'jack',
            'email': 'n.n@example.viindoo.com',
            'signature': '--\nJack',
            'notification_type': 'email',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_project_user.id])]
        })
        self.user_internal = self.env.ref('base.user_demo')
        self.user_internal.groups_id = [(6, 0, [user_group_employee.id])]

        self.task_3 = self.env['project.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test3', 'user_id': self.user_portal.id, 'project_id': self.project_pigs.id})
        self.task_4 = self.env['project.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test4', 'user_id': self.user_public.id, 'project_id': self.project_pigs.id})
        self.task_5 = self.env['project.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_id': False, 'project_id': self.project_pigs.id})
        self.task_6 = self.env['project.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_id': False, 'project_id': self.project_pigs.id})

        self.task_6.message_subscribe(partner_ids=[self.user_follower.partner_id.id])


@tagged('access_rights')
class TestPortalProject(TestPortalProjectBase):

    def test_user_internal_access_rights_project_project(self):
        project_1 = self.project_pigs

        project_1.privacy_visibility = 'employees'
        project_1.with_user(self.user_internal).read(['id'])

        project_1.privacy_visibility = 'portal'
        project_1.with_user(self.user_internal).read(['id'])

        project_1.privacy_visibility = 'followers'
        with self.assertRaises(AccessError):
            project_1.with_user(self.user_internal).read(['id'])

        self.task_6.user_id = self.user_internal
        project_1.with_user(self.user_internal).read(['id'])

        with self.assertRaises(AccessError):
            self.env['project.project'].with_user(self.user_internal).create({'name': 'project test'})
        with self.assertRaises(AccessError):
            project_1.with_user(self.user_internal).name = 'project1 test'
        with self.assertRaises(AccessError):
            project_1.with_user(self.user_internal).unlink()

    def test_user_internal_access_right_project_task(self):
        project_1 = self.project_pigs

        project_1.privacy_visibility = 'followers'
        with self.assertRaises(AccessError):
            self.task_5.with_user(self.user_internal).read(['id'])

        self.task_5.user_id = self.user_internal
        self.task_5.with_user(self.user_internal).read(['id'])
        self.task_5.with_user(self.user_internal).kanban_state = 'blocked'

        with self.assertRaises(AccessError):
            self.task_5.with_user(self.user_internal).name = 'task12345'
        with self.assertRaises(AccessError):
            self.task_5.with_user(self.user_internal).unlink()
        with self.assertRaises(AccessError):
            self.env['project.task'].with_user(self.user_internal).create({'name': 'task1', 'project_id': project_1.id})

        project_1.privacy_visibility = 'portal'
        self.task_3.with_user(self.user_internal).read(['id'])
        self.task_6.with_user(self.user_internal).read(['id'])

        with self.assertRaises(AccessError):
            self.task_3.with_user(self.user_internal).name = 'task12345'
        with self.assertRaises(AccessError):
            self.task_3.with_user(self.user_internal).unlink()
        with self.assertRaises(AccessError):
            self.env['project.task'].with_user(self.user_internal).create({'name': 'task1', 'project_id': project_1.id})


    @mute_logger('odoo.addons.base.models.ir_model')
    def test_employee_project_access_rights(self):
        pigs = self.project_pigs

        pigs.write({'privacy_visibility': 'employees'})
        # Do: Alfred reads project -> ok (employee ok employee)
        pigs.with_user(self.user_projectuser).read(['user_id'])
        # Test: all project tasks visible
        tasks = self.env['project.task'].with_user(self.user_projectuser).search([('project_id', '=', pigs.id)])
        test_task_ids = set([self.task_1.id, self.task_2.id, self.task_3.id, self.task_4.id, self.task_5.id, self.task_6.id])
        self.assertEqual(set(tasks.ids), test_task_ids,
                        'access rights: project user cannot see all tasks of an employees project')
        # Do: Bert reads project -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])
        # Do: Donovan reads project -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: project user is employee and can create a task
        tmp_task = self.env['project.task'].with_user(self.user_projectuser).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task',
            'project_id': pigs.id})
        tmp_task.with_user(self.user_projectuser).unlink()
        
    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_project_user_project_access_rights(self):
        pigs = self.project_pigs
        pigs.write({'user_id': self.user_projectuser.id, 'privacy_visibility': 'followers'})
        self.assertRaises(AccessError, pigs.with_user(self.user_employee1).write, {'name': 'Test write not ok'})
        pigs.with_user(self.user_projectuser).write({'name': 'Can write'})
        self.assertEqual(pigs.name, 'Can write')
        self.assertRaises(AccessError, pigs.with_user(self.user_projectuser2).write, {'name': 'Test write not ok'})

        # Not allow project user change others project's task stage
        self.project_goats.privacy_visibility = 'followers'
        stage_1 = self.env['project.task.type'].create({
            'name': 'Stage A',
            'project_ids': [(6, 0, self.project_goats.ids)]
        })
        task_1 = self.env['project.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Task 1',
            'project_id': self.project_goats.id,
            'stage_id': stage_1.id
        })
        task_1.message_subscribe(partner_ids=self.user_projectuser.ids)
        self.assertRaises(AccessError, stage_1.with_user(self.user_projectuser).write, {'name': 'Test write not ok'})

    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_followers_project_access_rights(self):
        pigs = self.project_pigs
        pigs.write({'privacy_visibility': 'followers'})
        pigs.flush(['privacy_visibility'])

        # Do: Jack reads project -> ok (task follower ok followers)
        pigs.with_user(self.user_follower).read(['user_id'])
        # Do: Jack edit project -> ko (task follower ko followers)
        self.assertRaises(AccessError, pigs.with_user(self.user_follower).write, {'name': 'Test Follow not ok'})
        # Do: Jack edit task not followed -> ko (task follower ko followers)
        self.assertRaises(AccessError, self.task_5.with_user(self.user_follower).write, {'name': 'Test Follow not ok'})
        # Do: Jack edit task followed-> ok (task follower ok followers)
        self.task_6.with_user(self.user_follower).write({'name': 'Test Follow ok'})

        # Do: Alfred reads project -> ko (employee ko followers)
        pigs.task_ids.message_unsubscribe(partner_ids=[self.user_projectuser.partner_id.id])
        self.assertRaises(AccessError, pigs.with_user(self.user_projectuser).read, ['user_id'])

        # Test: no project task visible
        tasks = self.env['project.task'].with_user(self.user_projectuser).search([('project_id', '=', pigs.id)])
        self.assertEqual(tasks, self.task_1,
                         'access rights: employee user should not see tasks of a not-followed followers project, only assigned')

        # Do: Bert reads project -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])

        # Do: Donovan reads project -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])

        pigs.message_subscribe(partner_ids=[self.user_projectuser.partner_id.id])

        # Do: Alfred reads project -> ok (follower ok followers)
        donkey = pigs.with_user(self.user_projectuser)
        donkey.invalidate_cache()
        donkey.read(['user_id'])

        # Do: Donovan reads project -> ko (public ko follower even if follower)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: project user is follower of the project and can create a task
        self.env['project.task'].with_user(self.user_projectuser).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task', 'project_id': pigs.id
        })
        # not follower user should not be able to create a task
        pigs.message_unsubscribe(partner_ids=[self.user_projectuser.partner_id.id])
        self.assertRaises(AccessError, self.env['project.task'].with_user(self.user_projectuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'project_id': pigs.id})

        # Do: project user can create a task without project
        self.assertRaises(AccessError, self.env['project.task'].with_user(self.user_projectuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'project_id': pigs.id})
