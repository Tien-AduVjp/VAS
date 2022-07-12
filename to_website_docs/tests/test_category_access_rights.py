from odoo.exceptions import AccessError, UserError
from odoo.tools import mute_logger
from odoo.tests import tagged

from .common import TestDocsCommon


@tagged('post_install', '-at_install')
class TestDocumentContentAccessRights(TestDocsCommon):

    def create_category(self, user, raise_exception=False):
        vals = {
            'name': 'General Debug',
            'parent_id': self.section_applications.id,
            'sequence': 10,
            'type': 'category',
            'document_type': 'link',
            }

        Category = self.env['website.doc.category']
        if raise_exception:
            self.assertRaises(AccessError, Category.with_user(user).create, vals)
        else:
            if user != self.editor_user:
                category = Category.with_user(user).create(vals)
                self.assertEqual('General Debug', category.name, 'Test create a document with %s not ok' % user.name)
            else:
                self.assertRaises(AccessError, Category.with_user(self.editor_user).create, vals)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_create_category(self):
        # Create docement with public / portal / internal user
        self.create_category(self.user_public, raise_exception=True)
        self.create_category(self.user_portal, raise_exception=True)
        self.create_category(self.user_internal, raise_exception=True)

        # Create Category with editor / reviewer / designer / manager user
        self.create_category(self.editor_user)
        self.create_category(self.reviewer_user)
        self.create_category(self.designer_user)
        self.create_category(self.manager_user)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_write_category(self):
        # Write with editor user
        self.assertRaises(AccessError, self.category_general.with_user(self.editor_user).write, {'name': "New Name"})
        # Write with reviewer user
        self.category_general.with_user(self.reviewer_user).write({'name': "New Name 1"})
        self.assertEqual("New Name 1", self.category_general.name, "Test write a category with Reviewer not ok")
        # Write with designer user
        self.category_general.with_user(self.designer_user).write({'name': "New Name 2"})
        self.assertEqual("New Name 2", self.category_general.name, "Test write a category with Designer not ok")
        # Write with manager user
        self.category_general.with_user(self.manager_user).write({'name': "New Name 3"})
        self.assertEqual("New Name 3", self.category_general.name, "Test write a category with Manager not ok")

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_category(self):
        # Unlink with editor user
        self.assertRaises(AccessError, self.category_general.with_user(self.editor_user).unlink)

        # Unlink with reviewer user
        self.assertRaises(AccessError, self.category_general_2.with_user(self.reviewer_user).unlink)
        self.assertRaises(UserError, self.category_general.with_user(self.reviewer_user).unlink)

        # Unlink with designer user
        self.assertRaises(AccessError, self.category_general_2.with_user(self.designer_user).unlink)
        self.assertRaises(UserError, self.category_general.with_user(self.designer_user).unlink)

        # Unlink with Manager
        self.assertEqual(True, self.category_general_2.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not ok')
        self.assertEqual(True, self.category_general.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not ok')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_create_setion(self):
        # Create docement with public / portal / internal user
        vals = {
            'name': 'Applications Debug',
            'parent_id': self.subject_user.id,
            'sequence': 10,
            'type': 'section',
            'document_type': 'link',
            'css_section_item': 'col-md-3',
            }
        Category = self.env['website.doc.category']
        self.assertRaises(AccessError, Category.with_user(self.user_public).create, vals)
        self.assertRaises(AccessError, Category.with_user(self.user_portal).create, vals)
        self.assertRaises(AccessError, Category.with_user(self.user_internal).create, vals)

        self.assertRaises(AccessError, Category.with_user(self.editor_user).create, vals)
        self.assertRaises(AccessError, Category.with_user(self.reviewer_user).create, vals)
        self.assertRaises(AccessError, Category.with_user(self.designer_user).create, vals)
        section = Category.with_user(self.manager_user).create(vals)
        self.assertEqual('Applications Debug', section.name, 'Test create a Section with Manager not ok')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_edit_setion(self):
        self.assertRaises(UserError, self.section_applications.with_user(self.editor_user).write, {'name':"New Name"})
        self.assertRaises(UserError, self.section_applications.with_user(self.reviewer_user).write, {'name':"New Name"})
        self.assertRaises(UserError, self.section_applications.with_user(self.designer_user).write, {'name':"New Name"})
        self.section_applications.with_user(self.manager_user).write({'name':"New Name"})
        self.assertEqual("New Name", self.section_applications.name, "Test Write with Manager not oke")

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_create_subject(self):
        vals = {
            'name': 'Odoo User Documentation',
            'sequence': 5,
            'description': 'An introduction guides for Odoo end-user.',
            'type': 'subject',
            'document_type': 'link',
            }
        Subject = self.env['website.doc.category']
        self.assertRaises(AccessError, Subject.with_user(self.user_public).create, vals)
        self.assertRaises(AccessError, Subject.with_user(self.user_portal).create, vals)
        self.assertRaises(AccessError, Subject.with_user(self.user_internal).create, vals)

        self.assertRaises(AccessError, Subject.with_user(self.editor_user).create, vals)
        self.assertRaises(AccessError, Subject.with_user(self.reviewer_user).create, vals)
        self.assertRaises(AccessError, Subject.with_user(self.designer_user).create, vals)
        subject = Subject.with_user(self.manager_user).create(vals)
        self.assertEqual('Odoo User Documentation', subject.name, 'Test create a Subject with Manager not ok')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_setion(self):
        self.assertRaises(AccessError, self.section_applications.with_user(self.editor_user).unlink)
        self.assertRaises(UserError, self.section_applications.with_user(self.reviewer_user).unlink)
        self.assertRaises(UserError, self.section_applications.with_user(self.designer_user).unlink)
        self.assertEqual(True, self.section_applications.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not ok')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_edit_subject(self):
        self.assertRaises(UserError, self.subject_user.with_user(self.editor_user).write, {'name':"New Name"})
        self.assertRaises(UserError, self.subject_user.with_user(self.reviewer_user).write, {'name':"New Name"})
        self.assertRaises(UserError, self.subject_user.with_user(self.designer_user).write, {'name':"New Name"})
        self.subject_user.with_user(self.manager_user).write({'name':"New Name"})
        self.assertEqual("New Name", self.subject_user.name, "Test Write with Manager not oke")

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_subject(self):
        self.assertRaises(AccessError, self.subject_user.with_user(self.editor_user).unlink)
        self.assertRaises(UserError, self.subject_user.with_user(self.reviewer_user).unlink)
        self.assertRaises(UserError, self.subject_user.with_user(self.designer_user).unlink)
        self.assertEqual(True, self.subject_user.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not ok')
