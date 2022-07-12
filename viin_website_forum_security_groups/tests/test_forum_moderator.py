from odoo.tests import tagged
from .common import TestForumSecurityCommon


@tagged('post_install', '-at_install', 'external', 'access_rights')
class TestForumModerator(TestForumSecurityCommon):

    @classmethod
    def setUpClass(cls):
        super(TestForumModerator, cls).setUpClass()
        cls.user_main = cls.user_employee

        TestUsersEnv = cls.env['res.users'].with_context({'no_reset_password': True})
        group_employee_id = cls.env.ref('base.group_user').id
        if not cls.env['res.users'].search([['login', '=', 'user_internal2@example.viindoo.com']]):
            cls.user_member = TestUsersEnv.create({
                'name': 'Armande Internal',
                'login': 'user_internal2',
                'email': 'user_internal2@example.viindoo.com',
                'karma': 0,
                'groups_id': [(6, 0, [group_employee_id])]
            })
        cls.forum.moderator_ids = cls.user_main
        cls.create_data()

    # test case 5
    def test_create_post(self):
        self.check_create_post()

    # test case 6, 7
    def test_vote(self):
        self.check_vote()

    # test case 8
    def test_edit_post(self):
        self.check_edit_post()

    # test case 9
    def test_close_post(self):
        self.check_close_post()

    # test case 10
    def test_delete_post(self):
        self.check_delete_post()

    # test case 12
    def test_post_toggle_correct(self):
        self.check_post_toggle_correct()

    # test case 13, 14
    def test_comment_post(self):
        self.check_comment_post()

    # test case 15
    def test_convert_answer_to_comment(self):
        self.check_convert_answer_to_comment()

    # test case 15
    def test_convert_comment_to_answer(self):
        self.check_convert_comment_to_answer()

    # test case 16
    def test_attach_link_image(self):
        self.check_attach_link_image()
   
    # test case 17
    def test_flag_a_post(self):
        self.check_flag()

    # test case 18
    def test_mark_a_post_as_offensive(self):
        self.check_mark_a_post_as_offensive()

    # test case 20, 21
    def test_tag(self):
        self.check_tag()

    # test case 28
    def test_delete_permission(self):
        self.check_delete_permission()

    def test_post_on_another_forum(self):
        self.check_post_on_another_forum()
