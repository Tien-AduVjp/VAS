from odoo.tests import tagged
from .common import TestForumSecurityCommon
from odoo.addons.website_forum.tests.common import KARMA


@tagged('post_install', '-at_install', 'external', 'access_rights')
class TestGroupForumAdministrator(TestForumSecurityCommon):

    @classmethod
    def setUpClass(cls):
        super(TestGroupForumAdministrator, cls).setUpClass()
        cls.user_main = cls.user_employee
        group_forum_admin = cls.env.ref('viin_website_forum_security_groups.group_forum_admin').id
        cls.user_main.write({
            'groups_id': [(6, 0, [group_forum_admin])]
        })
        TestUsersEnv = cls.env['res.users'].with_context({'no_reset_password': True})
        group_employee_id = cls.env.ref('base.group_user').id
        cls.user_member = TestUsersEnv.create({
            'name': 'Armande Internal',
            'login': 'user_internal2',
            'email': 'user_internal2@example.viindoo.com',
            'karma': 0,
            'groups_id': [(6, 0, [group_employee_id])]
        })
        cls.create_data()

    # test case 32
    def test_vote(self):
        self.check_vote()

    # test case 32
    def test_edit_post(self):
        self.check_edit_post()

    # test case 32
    def test_close_post(self):
        self.check_close_post()

    # test case 32
    def test_delete_post(self):
        self.check_delete_post()

    # test case 32
    def test_post_toggle_correct(self):
        self.check_post_toggle_correct()

    # test case 32
    def test_comment_post(self):
        self.check_comment_post()

    # test case 32
    def test_convert_answer_to_comment(self):
        self.check_convert_answer_to_comment()

    # test case 32
    def test_convert_comment_to_answer(self):
        self.check_convert_comment_to_answer()

    # test case 32
    def test_attach_link_image(self):
        self.check_attach_link_image()

    # test case 32
    def test_flag_a_post(self):
        self.check_flag()

    # test case 32
    def test_mark_a_post_as_offensive(self):
        self.check_mark_a_post_as_offensive()

    # test case 32
    def test_tag(self):
        self.check_tag()

    # test case 34, 35
    def test_create_forum(self):
        self.check_create_forum()
