from odoo.tests import tagged
from .common1 import TestDocsCommon1


@tagged('post_install', '-at_install')
class TestWebsiteDocsCategory(TestDocsCommon1):

    def test_func_search_document(self):
        # user_public can't see private doc
        documents = self.category_general_2.with_user(self.user_public).search_document()
        self.assertFalse(documents)
        # public all
        self.doc_2.category_id = self.category_general_2
        self.category_general_2.document_ids.state = 'approved'
        self.category_general_2.document_ids.content_ids.state = 'approved'
        self.category_general_2.document_ids.content_ids.action_publish_toggle()
        documents = self.category_general_2.with_user(self.user_public).search_document()
        self.assertTrue(['Python docs', "Welcome To Summoner's Rift"] == documents.mapped('name'))
        # Search by context odoo version. Result: Document with this odoo version
        document = self.category_general_2.with_user(self.user_public).with_context(odoo_version_str='22.0').search_document()
        self.assertTrue('Python docs' == document.name)
        # Editor can see all docs which belong to this category
        documents = self.category_general_2.with_user(self.editor_user).search_document()
        self.assertTrue(['Python docs', "Welcome To Summoner's Rift"] == documents.mapped('name'))

    def test_compute_odoo_version_on_category(self):
        # Change version of document_content => re-update version on its category
        old_version_ids = self.category_general_2.odoo_version_ids
        self.assertEqual(old_version_ids, self.odoo_version_v22)
        self.doc_content_5.odoo_version_id = self.odoo_version_v21.id
        new_version_ids = self.category_general_2.odoo_version_ids
        self.assertTrue(old_version_ids != new_version_ids)
        self.assertEqual(new_version_ids, self.odoo_version_v21)

        # Change document_id on document_content => re-update version on its category
        self.doc_content_5.document_id = self.doc_3
        self.assertNotEqual(self.category_general_2.document_ids, self.doc_3)
        self.assertFalse(self.category_general_2.odoo_version_ids)
