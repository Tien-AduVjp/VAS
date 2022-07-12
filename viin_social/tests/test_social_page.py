from odoo.tests.common import tagged
from .common import Common
from odoo.exceptions import UserError


@tagged('-at_install', 'post_install')
class TestSocialPage(Common):

    def test_compute_member_ids(self):
        # case 13:
        self.social_page_1.member_ids = self.user_editor
        self.social_page_1.assign_id = self.user_approve
        self.assertEqual(self.social_page_1.member_ids, self.user_editor + self.user_approve)

        self.social_media_1.assign_id = self.user_admin
        self.social_page_1.media_id = self.social_media_1
        self.assertEqual(self.social_page_1.member_ids, self.user_editor + self.user_approve + self.user_admin)

    def test_name_get(self):
        # case 14:
        self.social_media_1.name = 'Facebook Test'
        self.social_page_1.write({
            'media_id': self.social_media_1.id,
            'name': 'Page Test'
        })
        self.assertEqual(self.social_page_1.name_get()[0][1], '[Facebook Test] Page Test')

    def test_write(self):
        # case 15:
        self.social_page_1.with_user(self.user_admin).name = 'Page 1'
        self.assertEqual(self.social_page_1.name, 'Page 1')

        with self.assertRaises(UserError):
            self.social_page_1.with_user(self.user_approve).member_ids = self.user_editor

        self.social_page_1.assign_id = self.user_approve
        self.social_page_1.with_user(self.user_approve).member_ids = self.user_editor
        self.assertEqual(self.social_page_1.member_ids, self.user_editor)

    def test_get_social_page_message(self):
        # case 16:
        self.social_page_1.with_user(self.user_admin)._get_social_page_message()

        with self.assertRaises(UserError):
            self.social_page_1.with_user(self.user_editor)._get_social_page_message()

        self.social_page_1.assign_id = self.user_editor
        self.social_page_1.with_user(self.user_editor)._get_social_page_message()
