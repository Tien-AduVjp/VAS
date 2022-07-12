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

        # users
        cls.user_employee = cls.env['res.users'].create({
            'name': 'User Employee 1',
            'login': 'user_employee1',
            'email': 'user_employee1@example.viindoo.com',
            'groups_id': [(6, 0, cls.env.ref('hr_timesheet.group_hr_timesheet_user').ids)]
        })
        cls.user_projectmanager = cls.env['res.users'].create({
            'name': 'Project Manager',
            'login': 'project_manager',
            'email': 'project_manager@example.viindoo.com',
            'groups_id': [(6, 0, cls.env.ref('project.group_project_manager').ids)]
        })

        # Project: Office Design
        cls.project_1 = cls.env.ref('project.project_project_1')
        cls.project_1.write({
            'privacy_visibility': 'employees',
            'user_id': cls.user_employee.id,
            'project_user_full_access_rights': True,
        })
