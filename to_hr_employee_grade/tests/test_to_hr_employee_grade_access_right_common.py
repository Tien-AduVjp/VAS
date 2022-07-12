from odoo.tests.common import SavepointCase


class TestAccessRightCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRightCommon, cls).setUpClass()
        ResUsers = cls.env['res.users'].with_context(
            no_reset_password=True,
            tracking_disable=True
            )
        cls.internal_user = ResUsers.create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'internal_user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
        cls.hr_user = ResUsers.create({
            'name': 'Hr User ',
            'login': 'hr_user',
            'email': 'hr_user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('hr.group_hr_user').id])]
        })

        cls.intern = cls.env.ref('to_hr_employee_grade.intern_grade').with_context(tracking_disable=True)
