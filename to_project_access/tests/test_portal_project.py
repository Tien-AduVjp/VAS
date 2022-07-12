from odoo.tests import tagged
from odoo.exceptions import AccessError
from odoo.tools import mute_logger
from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestPortalProject(Common):

    def test_user_internal_access_rights_project_project(self):
        self.project_1.privacy_visibility = 'employees'
        self.project_1.with_user(self.user_internal).read(['id'])

        self.project_1.privacy_visibility = 'portal'
        self.project_1.with_user(self.user_internal).read(['id'])

        self.project_1.privacy_visibility = 'followers'
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).read(['id'])

        self.task_1.allowed_user_ids = [(4, self.user_internal.id)]
        self.task_1.user_id = self.user_internal

        self.project_1.with_user(self.user_internal).read(['id'])

        with self.assertRaises(AccessError):
            self.env['project.project'].with_user(self.user_internal).create({'name': 'project test'})
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).name = 'project1 test'
        # To avoid constraint: You cannot delete a project containing tasks
        self.project_1.sudo().tasks.unlink()
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).unlink()

    def test_user_internal_access_right_project_task(self):
        project_1 = self.project_1

        project_1.privacy_visibility = 'followers'
        with self.assertRaises(AccessError):
            self.task_1.with_user(self.user_internal).read(['id'])

        self.task_1.user_id = self.user_internal
        self.task_1.with_user(self.user_internal).read(['id'])
        self.task_1.with_user(self.user_internal).kanban_state = 'blocked'

        with self.assertRaises(AccessError):
            self.task_1.with_user(self.user_internal).name = 'task12345'
        with self.assertRaises(AccessError):
            self.task_1.with_user(self.user_internal).unlink()
        with self.assertRaises(AccessError):
            self.env['project.task'].with_user(self.user_internal).create({'name': 'task1', 'project_id': project_1.id})

        project_1.privacy_visibility = 'portal'
        self.task_1.with_user(self.user_internal).read(['id'])
        self.task_2.with_user(self.user_internal).read(['id'])

        with self.assertRaises(AccessError):
            self.task_1.with_user(self.user_internal).name = 'task12345'
        with self.assertRaises(AccessError):
            self.task_1.with_user(self.user_internal).unlink()
        with self.assertRaises(AccessError):
            self.env['project.task'].with_user(self.user_internal).create({'name': 'task1', 'project_id': project_1.id})

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_employee_project_access_rights(self):
        pigs = self.project_1

        pigs.write({'privacy_visibility': 'employees'})
        # Do: Alfred reads project -> ok (employee ok employee)
        pigs.with_user(self.user_projectuser).read(['id'])
        # Test: all project tasks visible
        tasks = self.env['project.task'].with_user(self.user_projectuser).search([('project_id', '=', pigs.id)])
        test_task_ids = {self.task_1.id, self.task_2.id}
        self.assertEqual(set(tasks.ids), test_task_ids,
                        'access rights: project user cannot see all tasks of an employees project')
        # Do: Bert reads project -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])
        # Do: Donovan reads project -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: project user is employee and can create / write / unlink a task
        pigs.write({'user_id': self.user_projectuser.id})
        tmp_task = self.env['project.task'].with_user(self.user_projectuser).create({
            'name': 'Pigs task',
            'project_id': pigs.id})
        tmp_task.with_user(self.user_projectuser).unlink()


    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_project_user_project_access_rights(self):
        pigs = self.project_1
        pigs.write({
            'user_id': self.user_projectuser.id,
            'privacy_visibility': 'followers',
            'project_user_full_access_rights': True,
        })
        self.assertRaises(AccessError, pigs.with_user(self.user_internal).write, {'name': 'Test write not ok'})
        pigs.with_user(self.user_projectuser).write({'name': 'Can write'})
        self.assertEqual(pigs.name, 'Can write')
        self.assertRaises(AccessError, pigs.with_user(self.user_projectuser2).write, {'name': 'Test write not ok'})

        # Not allow project user change others project's task stage
        self.project_2.privacy_visibility = 'followers'
        stage_1 = self.env['project.task.type'].create({
            'name': 'Stage A',
            'project_ids': [(6, 0, self.project_2.ids)]
        })
        task_1 = self.env['project.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Task 1',
            'project_id': self.project_2.id,
            'stage_id': stage_1.id
        })
        task_1.allowed_user_ids = [(4, self.user_projectuser.id)]
        self.assertRaises(AccessError, stage_1.with_user(self.user_projectuser).write, {'name': 'Test write not ok'})

    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_01_allowed_project_access_rights(self):
        pigs = self.project_1
        pigs.write({'privacy_visibility': 'followers'})
        pigs.flush(['privacy_visibility'])

        self.task_1.allowed_user_ids = [(4, self.user_projectuser.id)]

        # Do: Jack reads project -> ok (task is allowed)
        pigs.with_user(self.user_projectuser).read(['user_id'])
        # Do: Jack edit project -> not ok (task is not allowed)
        with self.assertRaises(AccessError):
            pigs.with_user(self.user_projectuser).write({'name': 'Test allowed not ok'})
        # Do: Jack edit task not allowed -> not ok (task is not allowed)
        with self.assertRaises(AccessError):
            self.task_3.with_user(self.user_projectuser).write({'name': 'Test allowed not ok'})
        # Do: Jack edit task allowed-> is not ok (task is allowed but user is not project manager)
        with self.assertRaises(AccessError):
            self.task_1.with_user(self.user_projectuser).write({'name': 'Test allowed ok'})

        # Do: Alfred reads project -> not ok (employee is allowed)
        pigs.task_ids.allowed_user_ids = [(6, 0, [])]
        self.assertRaises(AccessError, pigs.with_user(self.user_projectuser).read, ['user_id'])

    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_02_allowed_project_access_rights(self):
        pigs = self.project_1
        pigs.write({'privacy_visibility': 'followers'})
        pigs.flush(['privacy_visibility'])

        # Test: no project task visible
        self.task_1.user_id = self.user_projectuser
        task_1 = self.env['project.task'].with_user(self.user_projectuser).search([('id', '=', self.task_1.id)])
        self.assertTrue(
            task_1,
            'access rights: employee user should not see tasks of a not-allowed project, only assigned',
        )

        # Do: Bert reads project -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])

        # Do: Donovan reads project -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])

        pigs.write({
            'allowed_internal_user_ids': [(4, self.user_projectuser.id)],
            'user_id': self.user_projectuser.id,
            })

        # Do: Alfred reads project -> ok (follower ok followers)
        donkey = pigs.with_user(self.user_projectuser)
        donkey.invalidate_cache()
        donkey.read(['user_id'])

        # Do: Donovan reads project -> not ok (public user is not allowed)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: project user is allowed of the project and can create a task
        self.env['project.task'].with_user(self.user_projectuser).create({
            'name': 'Pigs task', 'project_id': pigs.id
        })
