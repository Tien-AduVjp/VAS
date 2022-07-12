from odoo.tests.common import tagged
from odoo.exceptions import AccessError, UserError
from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestToProjectAccess(Common):

    # ---------Internal User----------
    def test_01_internal_user_project_allowed_project(self):
        """ Test Allowed Internal User a project:
                - Internal User, Project privacy_visibility: 'followers', model: project.project
        """
        # project: 'privacy_visibility': 'followers', 'allowed_internal_user_ids': self.user_internal

        # not follow, cannot read
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).read(['id'])

        # Allowed project, can read
        self.project_1.allowed_internal_user_ids = [(4, self.user_internal.id)]
        self.project_1.with_user(self.user_internal).read(['id'])

    def test_02_internal_user_project_allowed_task(self):
        """ Test Allowed Internal User a task:
                - Internal User, Project privacy_visibility: 'followers', model: project.project
        """
        # not follow, cannot read
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).read(['id'])

        # allowed a task, can read
        self.task_1.allowed_user_ids = [(4, self.user_internal.id)]
        self.project_1.with_user(self.user_internal).read(['id'])

    def test_03_internal_user_project_allowed_access_right(self):
        """ Test No allowed Internal User Project / Task:
                - Internal User, Project privacy_visibility: 'followers', model: project.project
                - Expect: no access rights
        """
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).read(['id'])
        with self.assertRaises(AccessError):
            self.env['project.project'].with_user(self.user_internal).create({
                'name': 'Project 1',
                'privacy_visibility': 'followers',
            })
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).name = 'Project 123'
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).unlink()

    def test_04_internal_user_project_allowed_access_right(self):
        """ Test Allowed Internal User Project / Task:
                - Internal User, Project privacy_visibility: 'followers', model: project.project
                - Expect: Only have permission to read project
        """
        self.project_1.allowed_internal_user_ids = [(4, self.user_internal.id)]

        self.project_1.with_user(self.user_internal).read(['id'])

        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).name = 'Project 123'

        # To avoid constraint: You cannot delete a project containing tasks
        self.project_1.sudo().tasks.unlink()
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).unlink()

    def test_05_internal_user_project_employees_access_right(self):
        self.project_1.privacy_visibility = 'employees'
        self.project_1.with_user(self.user_internal).read(['id'])

        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).name = 'Project test'

        # To avoid constraint: You cannot delete a project containing tasks
        self.project_1.sudo().tasks.unlink()
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).unlink()

    def test_06_internal_user_project_portal_access_right(self):
        self.project_1.privacy_visibility = 'portal'
        self.project_1.with_user(self.user_internal).read(['id'])

        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).name = 'Project test'

        # To avoid constraint: You cannot delete a project containing tasks
        self.project_1.sudo().tasks.unlink()
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_internal).unlink()

    def test_01_internal_user_project_allowed_access_task(self):
        self.project_1.privacy_visibility = 'followers'

        # user internal follow task1
        self.task_1.allowed_user_ids = [(4, self.user_internal.id)]

        self.task_1.with_user(self.user_internal).read(['id'])
        with self.assertRaises(AccessError):
            self.task_2.with_user(self.user_internal).read(['id'])

        self.task_1.with_user(self.user_internal).kanban_state = 'done'
        self.task_1.with_user(self.user_internal).message_post(body='log message')

    def test_02_internal_user_project_employees_access_task(self):
        self.project_1.privacy_visibility = 'employees'

        self.task_1.with_user(self.user_internal).read(['id'])
        self.task_2.with_user(self.user_internal).read(['id'])

        self.task_1.with_user(self.user_internal).kanban_state = 'done'
        self.task_1.with_user(self.user_internal).message_post(body='log message')

    def test_03_internal_user_project_portal_access_task(self):
        self.project_1.privacy_visibility = 'portal'

        self.task_1.with_user(self.user_internal).read(['id'])
        self.task_2.with_user(self.user_internal).read(['id'])

        self.task_1.with_user(self.user_internal).kanban_state = 'done'
        self.task_1.with_user(self.user_internal).message_post(body='log message')

    # ---------Project User----------
    def test_01_project_user_project_allowed_access_right(self):
        self.project_1.privacy_visibility = 'followers'

        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_projectuser).read(['id'])

        with self.assertRaises(AccessError):
            self.task_1.with_user(self.user_projectuser).read(['id'])

    def test_02_project_user_project_allowed_access_right(self):
        self.project_1.privacy_visibility = 'followers'
        self.task_1.allowed_user_ids = [(4, self.user_projectuser.id)]

        self.project_1.with_user(self.user_projectuser).read(['id'])
        self.task_1.with_user(self.user_projectuser).read(['id'])

        # read unfollowed task
        with self.assertRaises(AccessError):
            self.task_2.with_user(self.user_projectuser).read(['id'])

    def test_03_project_user_project_allowed_access_right(self):
        # project user is the project manager of project_1, project_user_full_access_rights = False
        self.project_1.write({
            'privacy_visibility': 'followers',
            'user_id': self.user_projectuser.id,
            'project_user_full_access_rights': False
        })
        self.project_1.allowed_internal_user_ids = [(4, self.user_projectuser.id)]

        # Project User cannot edit `project_user_full_access_rights` field
        with self.assertRaises(UserError):
            self.project_1.with_user(self.user_projectuser).project_user_full_access_rights = True

        # Project User has full access right to tasks in project_1
        all_tasks = self.project_1.task_ids
        all_tasks.with_user(self.user_projectuser).read(['id'])
        all_tasks.with_user(self.user_projectuser).write({
            'name': 'test',
            'kanban_state': 'done'
        })
        all_tasks.with_user(self.user_projectuser).unlink()

        # Project User only has permission to read project_1
        self.project_1.with_user(self.user_projectuser).read(['id'])
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_projectuser).name = 'test'
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_projectuser).unlink()

        # Project User is the project manager of project_2, project_user_full_access_rights = True
        self.project_2.write({
            'privacy_visibility': 'followers',
            'user_id': self.user_projectuser.id,
            'project_user_full_access_rights': True
        })
        self.project_2.allowed_internal_user_ids = [(4, self.user_projectuser.id)]

        # Project User has full access right to project_2
        self.project_2.with_user(self.user_projectuser).read(['id'])
        self.project_2.with_user(self.user_projectuser).name = 'project test'

        self.project_2.task_ids.with_user(self.user_projectuser).unlink()
        self.project_2.with_user(self.user_projectuser).unlink()

    def test_04_project_user_create_project(self):
        # Project User create project_3, -> Project User has full access right to project_3
        project_3 = self.env['project.project'].with_user(self.user_projectuser).create({
            'name': 'project test',
            'privacy_visibility': 'followers',
        })

        self.assertEqual(project_3.user_id, self.user_projectuser)
        self.assertEqual(project_3.project_user_full_access_rights, True)

        project_3.with_user(self.user_projectuser).read(['id'])
        project_3.with_user(self.user_projectuser).name = 'project 33'
        project_3.with_user(self.user_projectuser).unlink()

    def test_05_project_user_project_employees(self):
        self.project_1.write({
            'privacy_visibility': 'employees',
            'user_id': self.user_projectuser.id,
            })

        self.project_1.with_user(self.user_projectuser).read(['id'])
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_projectuser).name = 'project test'
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_projectuser).unlink()

        all_tasks = self.project_1.task_ids
        all_tasks.with_user(self.user_projectuser).read(['id'])
        all_tasks.with_user(self.user_projectuser).name = 'task'
        all_tasks.with_user(self.user_projectuser).unlink()

    def test_06_project_user_project_portal(self):
        self.project_1.write({
            'privacy_visibility': 'portal',
            'user_id': self.user_projectuser.id,
            })

        self.project_1.with_user(self.user_projectuser).read(['id'])
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_projectuser).name = 'project test'
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_projectuser).unlink()

        all_tasks = self.project_1.task_ids
        all_tasks.with_user(self.user_projectuser).read(['id'])
        all_tasks.with_user(self.user_projectuser).name = 'task'
        all_tasks.with_user(self.user_projectuser).unlink()

    # ---------Project Admin----------
    def test_project_admin_access_right(self):
        project_3 = self.env['project.project'].with_user(self.user_projectuser).create({
            'name': 'Project 3',
            'task_ids': [(0, 0, {'name': 'task 1'})],
            'privacy_visibility': 'followers'
        })
        self.project_1.privacy_visibility = 'employees'
        self.project_2.privacy_visibility = 'portal'

        # Project Admin can edit `project_user_full_access_rights` field
        project_3.with_user(self.user_projectmanager).project_user_full_access_rights = True

        # Project Admin has full access right to all projects and tasks
        project_4 = self.env['project.project'].with_user(self.user_projectmanager).create({'name': 'Project 4'})
        self.env['project.task'].with_user(self.user_projectmanager).create({
            'name': 'task 5',
            'project_id': project_4.id
        })

        all_projects = self.project_1 + self.project_2 + project_3 + project_4
        all_tasks = all_projects.task_ids

        all_tasks.with_user(self.user_projectmanager).read(['id'])
        all_tasks.with_user(self.user_projectmanager).name = 'task'
        all_tasks.with_user(self.user_projectmanager).unlink()

        all_projects.with_user(self.user_projectmanager).read(['id'])
        all_projects.with_user(self.user_projectmanager).name = 'project'
        all_projects.with_user(self.user_projectmanager).unlink()

    # ---------Portal User----------
    def test_portal_user_project_access_rights(self):
        self.project_1.privacy_visibility = 'portal'
        self.task_1.allowed_user_ids = [(4, self.user_portal.id)]

        self.task_1.with_user(self.user_portal).read(['id'])
        self.task_1.with_user(self.user_portal).message_post(body='test')

        with self.assertRaises(AccessError):
            self.task_2.with_user(self.user_portal).read(['id'])
        with self.assertRaises(AccessError):
            self.project_1.with_user(self.user_portal).read(['id'])
        with self.assertRaises(AccessError):
            self.task_3.with_user(self.user_portal).read(['id'])
