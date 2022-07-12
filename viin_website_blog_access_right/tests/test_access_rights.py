from odoo.tests import SavepointCase, tagged
from odoo.exceptions import AccessError, AccessDenied


@tagged('post_install', '-at_install', 'access_rights')
class TestBlogAccessRights(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBlogAccessRights, cls).setUpClass()
        cls.home_page = cls.env.ref('website.homepage')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.user_demo.groups_id = [(4, cls.env.ref('website.group_website_publisher').id)]
        cls.blog = cls.env.ref('website_blog.blog_blog_1')

    def test_restricted_editor_with_own_blog_post(self):
        # create a new blog post
        blog_post = self.env['blog.post'].with_user(self.user_demo).create({
            'name': 'Blog Test',
            'blog_id': self.blog.id,
        })
        # write ok
        blog_post.name = 'Blog Test 2'
        # delete ok
        blog_post.unlink()
        # user publish blog

    def test_restricted_editor_with_own_blog_post_published(self):
        blog_post = self.env['blog.post'].with_user(self.user_demo).create({
            'name': 'Blog Test',
            'blog_id': self.blog.id,
        })
        # user publish blog

        with self.assertRaises(AccessError):
            blog_post.with_user(self.user_demo).is_published = True
        # admin publish blog
        try:
            blog_post.with_user(self.user_admin).is_published = True
        except AccessError:
            self.fail("Admin should be able to publish this page")
        # own blog, published => do not allow to edit
        with self.assertRaises(AccessError):
            blog_post.content = 'Blog Test content'

    def test_restricted_editor_with_another_blog(self):
        blog_post = self.env.ref('website_blog.blog_post_1').with_user(self.user_demo)
        with self.assertRaises(AccessError):
            blog_post.content = 'Blog Test content'
            blog_post.unlink()

    def test_restricted_editor_with_another_blog_follower(self):
        # user follow blog post unpublished => allow to edit, unlink
        blog_post = self.env.ref('website_blog.blog_post_1')
        blog_post.is_published = False
        blog_post.message_subscribe(self.user_demo.partner_id.ids)
        blog_post = blog_post.with_user(self.user_demo)
        blog_post.content = 'Blog Test content'
        blog_post.unlink()

    def test_restricted_editor_follow_another_post(self):
        with self.assertRaises(AccessDenied):
            self.env.ref('website_blog.blog_post_1').with_user(self.user_demo).message_subscribe(self.user_demo.ids)

    def test_restricted_editor_follow_own_post(self):
        blog_post = self.env['blog.post'].with_user(self.user_demo).create({
            'name': 'Blog Test',
            'blog_id': self.blog.id,
        })
        blog_post.message_unsubscribe(self.user_demo.ids)
        blog_post.message_subscribe(self.user_demo.ids)
