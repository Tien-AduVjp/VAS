from odoo.tests import SavepointCase, tagged
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install', 'access_rights')
class TestPageAccessRights(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPageAccessRights, cls).setUpClass()
        cls.home_page = cls.env.ref('website.homepage')
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_demo.groups_id = [(4, cls.env.ref('website.group_website_publisher').id)]

    def test_restricted_editor_with_own_page(self):
        # create a new page
        view = self.env['ir.ui.view'].with_user(self.user_demo).create({
            'name': 'View Test',
            'type': 'qweb',
            'arch_base': '<div>content</div>',
        })
        page = self.env['website.page'].with_user(self.user_demo).create({
            'name': 'My Page',
            'url': '/mypage',
            'view_id': view.id
        })
        # write own view, page
        view.write({
            'arch_base': '<div>content2</div>'
        })
        page.write({
            'url': '/my-page',
            'is_published': True
        })
        with self.assertRaises(AccessError):
            page.name = 'Ok'
            view.write({
                'arch_base': '<div>content3</div>'
            })

    def test_restricted_editor_with_another_page(self):
        view = self.env['ir.ui.view'].create({
            'name': 'View Test 2',
            'type': 'qweb',
            'arch_base': '<div>content</div>',
        })
        page = self.env['website.page'].create({
            'name': 'My Page 2',
            'url': '/mypage',
            'view_id': view.id
        }).with_user(self.user_demo)

        with self.assertRaises(AccessError):
            page.write({'arch_base': '<div>content 2</div>'})
            page.unlink()
