from odoo.exceptions import AccessError, UserError
from odoo.tools import mute_logger
from odoo.tests import tagged

from .common1 import TestDocsCommon1


@tagged('post_install', '-at_install', 'access_rights')
class TestDocumentAccessRights(TestDocsCommon1):
    
    def create_document(self, user, raise_exception=False):
        vals = {
            'name': 'Activate the Developer (Debug) Mode',
            'category_id': self.category_general.id,
            }
        Doc = self.env['website.document']
        if raise_exception:
            self.assertRaises(AccessError, Doc.with_user(user).create, vals)
        else:
            doc = Doc.with_user(user).create(vals)
            self.assertEqual('Activate the Developer (Debug) Mode', doc.name, 'Test create a document with %s not ok' % user.name)
            self.assertEqual(self.category_general, doc.category_id, 'Test create a document with %s not ok' % user.name)
     
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_create_document(self):
        # Create docement with public / portal / internal user
        self.create_document(self.user_public, raise_exception=True)
        self.create_document(self.user_portal, raise_exception=True)
        self.create_document(self.user_internal, raise_exception=True)
          
        # Create docement with editor / reviewer / designer / manager user
        self.create_document(self.editor_user)
        self.create_document(self.reviewer_user)
        self.create_document(self.designer_user)
        self.create_document(self.manager_user)
     
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_write_document_editor(self):
        self.doc.write({
            'author_id': self.admin.partner_id.id,
            'create_uid': self.admin.id,
            'user_id': False,
            'state': 'draft',
            })
            # No one was assigned
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).write, {'name': 'Test write with editor user not ok'})
         
            # Assign others to Document  
        self.doc.write({'user_id': self.editor_user_2.id})
        # Document: is not the author, assigned to other
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).write, {'name': 'Test write with Editor user not ok'})
        # Document: is the author, assigned to other
        self.doc.write({'author_id': self.manager_user.partner_id.id})
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).write, {'name': 'Test write with Editor user not ok'})
 
            # Assigned to Document
        self.doc.write({'user_id': self.editor_user.id})
        # Document: state = draft
        self.doc.with_user(self.editor_user).write({'name': 'Activate the Developer (Debug) Mode v1'})
        self.assertEqual('Activate the Developer (Debug) Mode v1', self.doc.name, 'Test write with Editor user not ok')
         
        # Document: state = confirmed
        self.doc.write({'state': 'confirmed'})
        self.doc.with_user(self.editor_user).write({'name': 'Activate the Developer (Debug) Mode v2'})
        self.assertEqual('Activate the Developer (Debug) Mode v2', self.doc.name, 'Test write with Editor user not ok')
         
        # Document: Approve the document
        with self.assertRaises(UserError):
            self.doc.with_user(self.editor_user).action_approve()
        self.assertNotEqual('approved', self.doc.state, 'Test write with Editor user not ok')
         
        # Document: Reject the document
        with self.assertRaises(UserError):
            self.doc.with_user(self.editor_user).action_reject()
        self.assertNotEqual('rejected', self.doc.state, 'Test write with Editor user not ok')
 
        # Document: state = rejected
        self.doc.write({'state': 'rejected'})
        self.doc.with_user(self.editor_user).write({'name': 'Activate the Developer (Debug) Mode v3'})
        self.assertEqual('Activate the Developer (Debug) Mode v3', self.doc.name, 'Test write with Editor user not ok')
         
        # Document: state = approved
        self.doc.write({'state': 'approved'})
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).write, {'name': 'Test write with Editor user not ok'})
         
        # Document: publish the document (with state = approved)
        self.doc.write({'can_publish': True})
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).write, {'is_published': True})
 
        # Document: state = Cancel
        self.doc.write({'state': 'cancelled'})
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).write, {'name': 'Test write with Editor user not ok'})
 
        # Document: published
        self.doc.write({'can_publish': True})
        self.doc.write({'is_published': True})
        self.assertRaises(UserError, self.doc.with_user(self.editor_user).write, {'name': 'Test write with Editor user not ok'})

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_write_document_reviewer(self):
        self.doc.write({
            'author_id': self.admin.partner_id.id,
            'create_uid': self.admin.id,
            'user_id': False,
            'state': 'draft',
            })
        # No one was assigned
        self.doc.with_user(self.reviewer_user).write({'name': "Rename Document v1"})
        self.assertEqual('Rename Document v1', self.doc.name, "Test write with Reviewer user not ok")
         
        # Assign others to Document
        # Assigned to editor
        self.doc.write({'user_id': self.editor_user.id})
        self.doc.with_user(self.reviewer_user).write({'name': "Rename Document v2"})
        self.assertEqual('Rename Document v2', self.doc.name, "Test write with Reviewer user not ok")
         
        # Assigned to Reviewer/Designer/Manager
        self.doc.write({'user_id': self.reviewer_user_2.id})
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).write, {'name': "Test write with Reviewer user not ok"})
        self.doc.write({'user_id': self.designer_user.id})
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).write, {'name': "Test write with Reviewer user not ok"})
        self.doc.write({'user_id': self.manager_user.id})
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).write, {'name': "Test write with Reviewer user not ok"})
         
        # Assigned to the Document
        # state = confirmed
        self.doc.write({'state': 'confirmed',
                        'user_id': self.reviewer_user.id, })
        self.doc.with_user(self.reviewer_user).write({'name': 'Rename Document v3'})
        self.assertEqual('Rename Document v3', self.doc.name, 'Test write with Reviewer user not ok')
         
        # state = rejected
        self.doc.write({'state': 'rejected'})
        self.doc.with_user(self.reviewer_user).write({'name': 'Rename Document v5'})
        self.assertEqual('Rename Document v5', self.doc.name, 'Test write with Reviewer user not ok')
         
        # state = cancelled
        self.doc.write({'state': 'cancelled'})
        self.doc.with_user(self.reviewer_user).write({'name': 'Rename Document v6'})
        self.assertEqual('Rename Document v6', self.doc.name, 'Test write with Reviewer user not ok')
         
        # state = approved
        self.doc.write({'state': 'approved'})
        self.doc.with_user(self.reviewer_user).write({'name': 'Rename Document v4'})
        self.assertEqual('Rename Document v4', self.doc.name, 'Test write with Reviewer user not ok')
 
        # Document: publish the document (with state = approved)
        with self.assertRaises(UserError):
            self.doc.with_user(self.reviewer_user).action_publish()
        self.assertNotEqual(True, self.doc.is_published, 'Test write with Reviewer user not ok')
 
        # Document: published
        self.doc.write({'is_published': True})
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).write, {'name': 'Test write with Reviewer user not ok'})

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_write_document_designer(self):
        self.doc.write({
            'author_id': self.admin.partner_id.id,
            'create_uid': self.admin.id,
            'user_id': False,
            'state': 'draft',
            })
         
        # No one was assigned
        self.doc.with_user(self.designer_user).write({'name': "Rename Document v1"})
        self.assertEqual('Rename Document v1', self.doc.name, "Test write with Designer user not ok")
         
        # Assign others to Document
        # Assigned to editor
        self.doc.write({'user_id': self.editor_user.id})
        self.doc.with_user(self.designer_user).write({'name': "Rename Document v2"})
        self.assertEqual('Rename Document v2', self.doc.name, "Test write with Designer user not ok")
         
        # Assigned to reviewer
        self.doc.write({'user_id': self.reviewer_user.id})
        self.doc.with_user(self.designer_user).write({'name': "Rename Document v2.2"})
        self.assertEqual('Rename Document v2.2', self.doc.name, "Test write with Designer user not ok")
         
        # Assigned to Designer/Manager
        self.doc.write({'user_id': self.designer_user_2.id})
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).write, {'name': "Test write with Designer user not ok"})
        self.doc.write({'user_id': self.manager_user.id})
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).write, {'name': "Test write with Designer user not ok"})
         
        # Assigned to the Document
        # state = confirmed
        self.doc.write({'state': 'confirmed',
                        'user_id': self.designer_user.id, })
        self.doc.with_user(self.designer_user).write({'name': 'Rename Document v3'})
        self.assertEqual('Rename Document v3', self.doc.name, 'Test write with Designer user not ok')
         
        # state = rejected
        self.doc.write({'state': 'rejected'})
        self.doc.with_user(self.designer_user).write({'name': 'Rename Document v5'})
        self.assertEqual('Rename Document v5', self.doc.name, 'Test write with Designer user not ok')
         
        # state = cancelled
        self.doc.write({'state': 'cancelled'})
        self.doc.with_user(self.designer_user).write({'name': 'Rename Document v6'})
        self.assertEqual('Rename Document v6', self.doc.name, 'Test write with Designer user not ok')
         
        # state = approved
        self.doc.write({'state': 'approved'})
        self.doc.with_user(self.designer_user).write({'name': 'Rename Document v4'})
        self.assertEqual('Rename Document v4', self.doc.name, 'Test write with Designer user not ok')
         
        # Document: publish the document (with state = approved)
        # content: published -> document: published
        self.doc_content.write({
            'author_id': self.designer_user.partner_id.id,
            'state': 'approved',
            })
        self.doc_content.with_user(self.designer_user).action_publish()
        self.assertEqual(True, self.doc.is_published, 'Test write with Designer user not ok')
        
        # Document: published
        self.doc.with_user(self.designer_user).write({'name': 'Rename Document 1'})
        self.assertEqual("Rename Document 1", self.doc.name, 'Test write with Designer user not ok')

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_write_document_manager(self):
        self.doc.write({
            'author_id': self.admin.partner_id.id,
            'create_uid': self.admin.id,
            'user_id': False,
            'state': 'draft',
            })
        # No one was assigned
        self.doc.with_user(self.manager_user).write({'name': "Rename Document v1"})
        self.assertEqual('Rename Document v1', self.doc.name, "Test write with Manager user not ok")
         
        # Assign others to Document
        # Assigned to editor
        self.doc.write({'user_id': self.editor_user.id})
        self.doc.with_user(self.manager_user).write({'name': "Rename Document v2"})
        self.assertEqual('Rename Document v2', self.doc.name, "Test write with Manager user not ok")
         
        # Assigned to reviewer
        self.doc.write({'user_id': self.reviewer_user.id})
        self.doc.with_user(self.manager_user).write({'name': "Rename Document v2.2"})
        self.assertEqual('Rename Document v2.2', self.doc.name, "Test write with Manager user not ok")
         
        # Assigned to designer
        self.doc.write({'user_id': self.designer_user.id})
        self.doc.with_user(self.manager_user).write({'name': "Rename Document v2.3"})
        self.assertEqual('Rename Document v2.3', self.doc.name, "Test write with Manager user not ok")
         
        # Assigned to the Document
        # state = confirmed
        self.doc.write({'state': 'confirmed',
                        'user_id': self.manager_user.id, })
        self.doc.with_user(self.manager_user).write({'name': 'Rename Document v3'})
        self.assertEqual('Rename Document v3', self.doc.name, 'Test write with Manager user not ok')
         
        # state = rejected
        self.doc.write({'state': 'rejected'})
        self.doc.with_user(self.manager_user).write({'name': 'Rename Document v5'})
        self.assertEqual('Rename Document v5', self.doc.name, 'Test write with Manager user not ok')
         
        # state = cancelled
        self.doc.write({'state': 'cancelled'})
        self.doc.with_user(self.manager_user).write({'name': 'Rename Document v6'})
        self.assertEqual('Rename Document v6', self.doc.name, 'Test write with Manager user not ok')
         
        # state = approved
        self.doc.write({'state': 'approved'})
        self.doc.with_user(self.manager_user).write({'name': 'Rename Document v4'})
        self.assertEqual('Rename Document v4', self.doc.name, 'Test write with Manager user not ok')
         
        # Document: publish the document (with state = approved)
        # content: published -> document: published
        self.doc_content.write({
            'author_id': self.designer_user.partner_id.id,
            'state': 'approved',
            })
        self.doc_content.with_user(self.manager_user).action_publish()
        self.assertEqual(True, self.doc.is_published, 'Test write with Manager user not ok')
         
        # Document: published
        self.doc.with_user(self.manager_user).write({'name': 'Rename Document v7'})
        self.assertEqual("Rename Document v7", self.doc.name, 'Test write with Manager user not ok')

    """
    Test unlink
    """

    def create_docs(self, state='draft', author_id=False, user_id=False):
        data = {
            'name': 'Activate the Developer (Debug) Mode',
            'category_id': self.category_general.id,
            'author_id': author_id or self.editor_user.partner_id.id,
            'create_uid': user_id or self.editor_user.id,
            'user_id': user_id or self.editor_user.id,
            'state': state,
            }
        return self.env['website.document'].create(data)
         
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_document_editor(self):
        self.doc.write({
            'author_id': self.admin.partner_id.id,
            'create_uid': self.admin.id,
            'user_id': False,
            'state': 'draft',
            })
  
        """Author is the other"""
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).unlink)
  
        """Is the Author"""
        self.doc.write({'author_id': self.editor_user.partner_id.id})
        # No one was assigned
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).unlink)
          
        # Assign others to Document
        self.doc.write({'user_id': self.editor_user_2.id})
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).unlink)
  
            # Assigned to Document
        # state = draft
        doc = self.create_docs()
        self.assertEqual(True, doc.with_user(self.editor_user).unlink(), 'Test Unlink with Editor user not ok')
  
        # state = confirmed
        doc = self.create_docs('confirmed')
        self.assertEqual(True, doc.with_user(self.editor_user).unlink(), 'Test Unlink with Editor user not ok')
          
        # state = rejected
        doc = self.create_docs('rejected')
        self.assertEqual(True, doc.with_user(self.editor_user).unlink(), 'Test Unlink with Editor user not ok')
          
        # state = approved
        self.doc.write({'state': 'approved'})
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).unlink)
          
        # state = cancelled
        self.doc.write({'state': 'cancelled'})
        self.assertRaises(AccessError, self.doc.with_user(self.editor_user).unlink)
          
        # Published
        self.doc.write({'can_publish': True})
        self.doc.write({'is_published': True})
        self.assertRaises(UserError, self.doc.with_user(self.editor_user).unlink)

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_document_reviewer(self):
        # Author: Editor, Assign: Editor/Reviewer/Reviewer 2/Designer/Manager
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.editor_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')   
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.reviewer_user_2.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
         
        # Author: Reviewer 2, Assign: Editor/Reviewer/Designer/Manager
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.editor_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.reviewer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
         
        # Author: Designer, Assign: Editor/Reviewer/Designer/Manager
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.editor_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
 
        # Author: Manager, Assign: Editor/Reviewer/Designer/Manager
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.editor_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
         
        # Author: Reviewer, Assign: Editor/Reviewer/Reviewer 2/Designer/Manager
        doc = self.create_docs(author_id=self.reviewer_user.partner_id.id, user_id=self.editor_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')
        doc = self.create_docs(author_id=self.reviewer_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')  
        doc = self.create_docs(author_id=self.reviewer_user.partner_id.id, user_id=self.reviewer_user_2.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.reviewer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
        doc = self.create_docs(author_id=self.reviewer_user.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
         
        # Author: Reviewer, Assign: Reviewer, State: draft, confirmed, approved, rejected, cancelled, Publish: True
        doc = self.create_docs(state='confirmed', author_id=self.reviewer_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')
        doc = self.create_docs(state='approved', author_id=self.reviewer_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')
        doc = self.create_docs(state='rejected', author_id=self.reviewer_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')
        doc = self.create_docs(state='cancelled', author_id=self.reviewer_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.reviewer_user).unlink(), 'Test Unlink with Reviewer user not ok')
        doc = self.create_docs(state='approved', author_id=self.reviewer_user.partner_id.id, user_id=self.reviewer_user.id)
        # content: published -> document: published
        self.doc_content.write({
            'author_id': self.reviewer_user.partner_id.id,
            'document_id': doc.id,
            'state': 'approved',
            })
        self.doc_content.with_user(self.manager_user).action_publish()
        self.assertRaises(UserError, self.doc.with_user(self.reviewer_user).unlink)
    
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_document_designer(self):
        # Author: Editor, Assign: Editor/Reviewer/Designer/Designer 2/Manager
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.editor_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')   
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.designer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.designer_user_2.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.editor_user.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
         
        # Author: Reviewer, Assign: Editor/Reviewer/Designer/Designer 2/Manager
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.editor_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.designer_user_2.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.reviewer_user_2.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
         
        # Author: Designer, Assign: Editor/Reviewer/Designer/Designer2/Manager
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.editor_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.designer_user_2.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.designer_user.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
         
        # Author: Manager, Assign: Editor/Reviewer/Designer/Manager
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.editor_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.reviewer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.manager_user.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
         
        # Author: Designer 2, Assign: Editor/Reviewer/Designer/Manager
        doc = self.create_docs(author_id=self.designer_user_2.partner_id.id, user_id=self.editor_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.designer_user_2.partner_id.id, user_id=self.reviewer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.designer_user_2.partner_id.id, user_id=self.designer_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
        doc = self.create_docs(author_id=self.designer_user_2.partner_id.id, user_id=self.manager_user.id)
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
         
        # Author: Designer, Assign: Designer, State: draft, confirmed, approved, rejected, cancelled, Publish: True
        doc = self.create_docs(state='confirmed', author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(state='approved', author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(state='rejected', author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(state='cancelled', author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertEqual(True, doc.with_user(self.designer_user).unlink(), 'Test Unlink with Designer user not ok')
        doc = self.create_docs(state='approved', author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        # content: published -> document: published
        self.doc_content.write({
            'author_id': self.designer_user.partner_id.id,
            'document_id': doc.id,
            'state': 'approved',
            })
        self.doc_content.with_user(self.manager_user).action_publish()
        self.assertRaises(UserError, self.doc.with_user(self.designer_user).unlink)
    
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_unlink_document_manager(self):
        doc = self.create_docs(state='approved', author_id=self.designer_user.partner_id.id, user_id=self.designer_user.id)
        self.assertEqual(True, doc.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not ok')
        doc = self.create_docs(state='approved', author_id=self.manager_user.partner_id.id, user_id=self.manager_user.id)
        self.assertEqual(True, doc.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not ok')
        doc = self.create_docs(state='approved', author_id=self.manager_user.partner_id.id, user_id=self.manager_user.id)
        # content: published -> document: published
        self.doc_content.write({
            'author_id': self.designer_user.partner_id.id,
            'document_id': doc.id,
            'state': 'approved',
            })
        self.doc_content.with_user(self.manager_user).action_publish()
        self.assertEqual(True, doc.with_user(self.manager_user).unlink(), 'Test Unlink with Manager user not ok')

    def test_copy_document_editor(self):
        # Case: Editor duplicate another document
        # Result: Success
        doc_copy = self.doc.with_user(self.editor_user).copy()
        # Case: Editor edit the document duplicated above
        # Result: Success
        doc_copy.name = 'Doc copy name'
        # Case: Editor delete the document duplicated above
        # Result: Success
        doc_copy.unlink()

    def test_copy_document_reviewer(self):
        # Case: Reviewer duplicate another document
        # Result: Success
        doc_copy = self.doc.with_user(self.reviewer_user).copy()
        # Case: Reviewer edit the document duplicated above
        # Result: Success
        doc_copy.name = 'Doc copy name'
        # Case: Reviewer delete the document duplicated above
        # Result: Success
        doc_copy.unlink()

    def test_copy_document_designer(self):
        # Case: Designer duplicate another document
        # Result: Success
        doc_copy = self.doc.with_user(self.designer_user).copy()
        # Case: Designer edit the document duplicated above
        # Result: Success
        doc_copy.name = 'Doc copy name'
        # Case: Designer delete the document duplicated above
        # Result: Success
        doc_copy.unlink()

    def test_copy_document_manager(self):
        # Manager: Manager duplicate another document
        # Result: Success
        doc_copy = self.doc.with_user(self.manager_user).copy()
        # Case: Manager edit the document duplicated above
        # Result: Success
        doc_copy.name = 'Doc copy name'
        # Case: Manager delete the document duplicated above
        # Result: Success
        doc_copy.unlink()
