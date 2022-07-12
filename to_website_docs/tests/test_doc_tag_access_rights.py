from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import TestDocsCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestDocTagAccessRights(TestDocsCommon):

    def create_tag_with_user(self, user):
        return self.env['website.doc.tag'].with_user(user).create({'name': 'tag_public_%s' % user.id})

    def test_access_tag(self):
        # create
        with self.assertRaises(AccessError):
            self.create_tag_with_user(self.user_public)
            self.create_tag_with_user(self.user_portal)
            self.create_tag_with_user(self.user_internal)

        own_tag_1 = self.create_tag_with_user(self.editor_user)
        own_tag_2 = self.create_tag_with_user(self.reviewer_user)
        own_tag_3 = self.create_tag_with_user(self.designer_user)
        own_tag_4 = self.create_tag_with_user(self.manager_user)

        # write
        with self.assertRaises(AccessError):
            self.tag_1.with_user(self.user_public).write({'name': 'own_tag_1'})
            self.tag_1.with_user(self.user_portal).write({'name': 'own_tag_2'})
            self.tag_1.with_user(self.user_internal).write({'name': 'own_tag_3'})

        own_tag_1.with_user(self.editor_user).write({'name': 'own_tag_4'})
        own_tag_2.with_user(self.reviewer_user).write({'name': 'own_tag_5'})
        own_tag_3.with_user(self.designer_user).write({'name': 'own_tag_6'})
        own_tag_4.with_user(self.manager_user).write({'name': 'own_tag_7'})

        # unlink
        with self.assertRaises(AccessError):
            self.tag_1.with_user(self.user_public).unlink()
            self.tag_1.with_user(self.user_portal).unlink()
            self.tag_1.with_user(self.user_internal).unlink()

        own_tag_1.with_user(self.editor_user).unlink()
        own_tag_2.with_user(self.reviewer_user).unlink()
        own_tag_3.with_user(self.designer_user).unlink()
        own_tag_4.with_user(self.manager_user).unlink()
