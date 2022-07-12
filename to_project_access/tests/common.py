from odoo.tests.common import SavepointCase


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.user_public = cls.env['res.users'].create({
            'name': 'Bert Tartignole',
            'login': 'bert',
            'email': 'b.t@example.viindoo.com',
            'signature': 'SignBert',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_public').id])]
        })
        cls.user_internal = cls.env['res.users'].create({
            'name': 'Test Employee',
            'login': 'test.employee',
            'email': 'test.employee@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
        cls.user_projectuser = cls.env['res.users'].create({
            'name': 'ProjectUser ',
            'login': 'project.user',
            'email': 'project.user2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('project.group_project_user').id])]
        })
        cls.user_projectuser2 = cls.env['res.users'].create({
            'name': 'ProjectUser 2',
            'login': 'project.user2',
            'email': 'project.user2@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('project.group_project_user').id])]
        })
        cls.user_projectmanager = cls.env['res.users'].create({
            'name': 'Bastien ProjectManager',
            'login': 'bastien',
            'email': 'bastien.projectmanager@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('project.group_project_manager').id])]
        })
        cls.user_portal = cls.env['res.users'].create({
            'name': 'Chell Gladys',
            'login': 'chell',
            'email': 'chell@gladys.portal',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]
        })
        cls.user_noone = cls.env['res.users'].create({
            'name': 'Noemie NoOne',
            'login': 'noemie',
            'email': 'n.n@example.viindoo.com',
            'groups_id': [(6, 0, [])]
        })

        cls.type_ids = cls.env['project.task.type'].create([
            {'name': 'New'},
            {'name': 'Test'},
            {'name': 'Done'}
        ])

        cls.project_1 = cls.env['project.project'].create({
            'name': 'Project 1',
            'privacy_visibility': 'followers',
            'allowed_internal_user_ids': False,
            'type_ids': cls.type_ids
        })
        cls.project_2 = cls.env['project.project'].create({
            'name': 'Project 2',
            'privacy_visibility': 'followers',
            'allowed_internal_user_ids': False,
            'type_ids': cls.type_ids
        })

        cls.task_1 = cls.env['project.task'].create({
            'name': 'Task 1',
            'project_id': cls.project_1.id
        })
        cls.task_2 = cls.env['project.task'].create({
            'name': 'Task 2',
            'project_id': cls.project_1.id
        })
        cls.task_3 = cls.env['project.task'].create({
            'name': 'Task 3',
            'project_id': cls.project_2.id
        })
        cls.task_4 = cls.env['project.task'].create({
            'name': 'Task 4',
            'project_id': cls.project_2.id
        })
