from odoo.exceptions import AccessError, UserError
from odoo.tools import mute_logger, html2plaintext
from odoo.tests import tagged

from .common1 import TestDocsCommon1


@tagged('post_install', '-at_install', 'access_rights')
class TestDocumentContentAccessRights(TestDocsCommon1):
    
    def create_document_content(self, user, raise_exception=False):
        vals = {
            'document_id': self.doc.id,
            'fulltext': 'The Developer or Debug Mode gives you access to extra and advanced tools...',
            }
         
        Content = self.env['website.document.content']
         
        if raise_exception:
            self.assertRaises(AccessError, Content.with_user(user).create, vals)
        else:
            content = Content.with_user(user).create(vals)
            self.assertEqual('The Developer or Debug Mode gives you access to extra and advanced tools...', html2plaintext(content.fulltext), 'Test create a document content with %s not ok' % user.name)
            self.assertEqual(self.doc, content.document_id, 'Test create a document with %s not ok' % user.name)
     
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_create_document_content(self):
        # Create docement with public / portal / internal user
        self.create_document_content(self.user_public, raise_exception=True)
        self.create_document_content(self.user_portal, raise_exception=True)
        self.create_document_content(self.user_internal, raise_exception=True)
         
        # Create docement with editor / reviewer / designer / manager user
        self.create_document_content(self.editor_user)
        self.create_document_content(self.reviewer_user)
        self.create_document_content(self.designer_user)
        self.create_document_content(self.manager_user)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_write_document_content(self):
        self.doc.write({
            'author_id': self.manager_user.partner_id.id,
            'user_id': self.editor_user.id,
            'state': 'draft',
            })
        self.doc_content.with_user(self.manager_user).write({
            'author_id': self.admin.partner_id.id,
            'state': 'draft',
            })
        # No one was assigned to doc, User: Editor/Reviewer/Designer/Manager
        self.doc.write({'user_id': False})
        self.assertRaises(AccessError, self.doc_content.with_user(self.editor_user).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.reviewer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Reviewer user not ok')
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        # Editor assigned to Doc, User: Editor/Editor 2/Reviewer/Designer/Manager
        self.doc.write({'user_id': self.editor_user.id})
        self.doc_content.with_user(self.editor_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with editor user not ok')
        self.assertRaises(AccessError, self.doc_content.with_user(self.editor_user_2).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.reviewer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Reviewer user not ok')
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        # Reviewer assigned to Doc, User: Editor/Reviewer/Reviewer 2/Designer/Manager
        self.doc.write({'user_id': self.reviewer_user.id})
        self.doc_content.write({'state': 'draft'})
         
        self.assertRaises(AccessError, self.doc_content.with_user(self.editor_user).write, {'fulltext': "new Text"})
        self.assertRaises(UserError, self.doc_content.with_user(self.reviewer_user_2).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.reviewer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Reviewer user not ok')
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        # Designer assigned to Doc, User: Editor/Reviewer/Designer 2/Designer/Manager
        self.doc.write({'user_id': self.designer_user.id})
        self.assertRaises(AccessError, self.doc_content.with_user(self.editor_user).write, {'fulltext': "new Text"})
        self.assertRaises(UserError, self.doc_content.with_user(self.reviewer_user).write, {'fulltext': "new Text"})
        self.assertRaises(UserError, self.doc_content.with_user(self.designer_user_2).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        # Manager assigned to Doc, User: Editor/Reviewer/Designer/Manager
        self.doc.write({'user_id': self.manager_user.id})
        self.assertRaises(AccessError, self.doc_content.with_user(self.editor_user).write, {'fulltext': "new Text"})
        self.assertRaises(UserError, self.doc_content.with_user(self.reviewer_user).write, {'fulltext': "new Text"})
        self.assertRaises(UserError, self.doc_content.with_user(self.designer_user_2).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        # Check State: draft/confirmed/approved/rejected/cancelled, Publish: True
        self.doc.write({'user_id': self.editor_user.id,
                        'author_id': self.editor_user.partner_id.id})
        self.doc_content.with_user(self.manager_user).write({
                        'author_id': self.admin.partner_id.id,
                        'state': 'confirmed'
                    })
        self.doc_content.with_user(self.editor_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with editor user not ok')
        self.doc_content.with_user(self.reviewer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Reviewer user not ok')
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        self.doc_content.write({'state': 'rejected'})
        self.doc_content.with_user(self.editor_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with editor user not ok')
        self.doc_content.with_user(self.reviewer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Reviewer user not ok')
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        self.doc_content.write({'state': 'cancelled'})
        self.assertRaises(AccessError, self.doc_content.with_user(self.editor_user).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.reviewer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Reviewer user not ok')
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        self.doc_content.write({'state': 'approved'})
        self.assertRaises(AccessError, self.doc_content.with_user(self.editor_user).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.reviewer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Reviewer user not ok')
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
         
        self.doc_content.write({'is_published': True})
        self.assertRaises(UserError, self.doc_content.with_user(self.editor_user).write, {'fulltext': "new Text"})
        self.assertRaises(UserError, self.doc_content.with_user(self.reviewer_user).write, {'fulltext': "new Text"})
        self.doc_content.with_user(self.designer_user).write({'fulltext': "new Text 1"})
        self.assertEqual("new Text 1", html2plaintext(self.doc_content.fulltext), 'Test write with Designer user not ok')
        self.doc_content.with_user(self.manager_user).write({'fulltext': "new Text"})
        self.assertEqual("new Text", html2plaintext(self.doc_content.fulltext), 'Test write with Manager user not ok')
    
    """
    For Unlink
    """

    def create_doc_content(self, doc_author=False, user_id=False, state='draft'):
        data_doc = {
            'name': 'Activate the Developer (Debug) Mode',
            'category_id': self.category_general.id,
            'author_id': doc_author or self.editor_user.partner_id.id,
            'user_id': user_id or self.editor_user.id,
            'state': state,
            }
        doc = self.env['website.document'].create(data_doc)
        data_doc_content = {
            'document_id': doc.id,
            'fulltext': 'The Developer or Debug Mode gives you access to extra and advanced tools...',
            'author_id': doc_author or self.editor_user.partner_id.id,
            'state': state,
            }
        return self.env['website.document.content'].create(data_doc_content)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_document_content(self):
        # if user == author => Unlink
        # else: check document (test unlink documents)
        # State, Publish
        
        # Editor
        content = self.create_doc_content()
        self.assertRaises(AccessError, content.with_user(self.editor_user_2).unlink)
        self.assertEqual(True, content.with_user(self.editor_user).unlink(), 'Test Unlink not oke')
        
        # Reviewer
        content = self.create_doc_content(self.reviewer_user.partner_id.id, self.reviewer_user.id)
        self.assertRaises(UserError, content.with_user(self.reviewer_user_2).unlink)
        self.assertEqual(True, content.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not oke')
        
        # Designer
        content = self.create_doc_content(self.designer_user.partner_id.id, self.designer_user.id)
        self.assertRaises(UserError, content.with_user(self.designer_user_2).unlink)
        self.assertEqual(True, content.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not oke')
        
        # Manager
        content = self.create_doc_content(self.designer_user.partner_id.id, self.designer_user.id)
        self.assertEqual(True, content.with_user(self.manager_user).unlink(), 'Test Unlink Manager user not oke')
        
        # State: draft/confirmed/approved/rejected/cancelled, Publish: True
        content = self.create_doc_content(state='confirmed')
        self.assertEqual(True, content.with_user(self.editor_user).unlink(), 'Test Unlink with Editor user not oke')
        content = self.create_doc_content(state='confirmed')
        self.assertEqual(True, content.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not oke')
        content = self.create_doc_content(state='confirmed')
        self.assertEqual(True, content.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not oke')
        content = self.create_doc_content(state='confirmed')
        self.assertEqual(True, content.with_user(self.manager_user).unlink(), 'Test Unlink Manager user not oke')
        
        content = self.create_doc_content(state='rejected')
        self.assertEqual(True, content.with_user(self.editor_user).unlink(), 'Test Unlink with Editor user not oke')
        content = self.create_doc_content(state='rejected')
        self.assertEqual(True, content.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not oke')
        content = self.create_doc_content(state='rejected')
        self.assertEqual(True, content.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not oke')
        content = self.create_doc_content(state='rejected')
        self.assertEqual(True, content.with_user(self.manager_user).unlink(), 'Test Unlink Manager user not oke')
        
        content = self.create_doc_content(state='cancelled')
        self.assertRaises(AccessError, content.with_user(self.editor_user).unlink)
        self.assertEqual(True, content.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not oke')
        content = self.create_doc_content(state='cancelled')
        self.assertEqual(True, content.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not oke')
        content = self.create_doc_content(state='cancelled')
        self.assertEqual(True, content.with_user(self.manager_user).unlink(), 'Test Unlink Manager user not oke')
        
        content = self.create_doc_content(state='approved')
        self.assertRaises(AccessError, content.with_user(self.editor_user).unlink)
        self.assertEqual(True, content.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not oke')
        content = self.create_doc_content(state='approved')
        self.assertEqual(True, content.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not oke')
        content = self.create_doc_content(state='approved')
        self.assertEqual(True, content.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not oke')
        
        content = self.create_doc_content(state='approved')
        content.write({'is_published': True})
        self.assertRaises(UserError, content.with_user(self.editor_user).unlink)
        self.assertRaises(UserError, content.with_user(self.reviewer_user).unlink)
        self.assertRaises(UserError, content.with_user(self.designer_user).unlink)
        self.assertEqual(True, content.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not oke')
