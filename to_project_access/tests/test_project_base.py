# -*- coding: utf-8 -*-

from odoo.addons.project.tests import test_project_base

class TestProjectBase(test_project_base.TestProjectBase):

    @classmethod
    def setUpClass(cls):
        super(TestProjectBase, cls).setUpClass()

        user_group_employee = cls.env.ref('base.group_user')
        user_group_project_user = cls.env.ref('project.group_project_user')

        Users = cls.env['res.users'].with_context({'no_reset_password': True})

        cls.user_employee1 = Users.create({
            'name': 'Test Employee',
            'login': 'test.employee',
            'email': 'test.employee@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id,])]
        })
        cls.user_projectuser2 = Users.create({
            'name': 'ProjectUser 2',
            'login': 'project.user2',
            'email': 'project.user2@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_project_user.id])]
        })
