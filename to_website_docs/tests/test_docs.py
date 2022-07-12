from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common1 import TestDocsCommon1


@tagged('post_install', '-at_install')
class TestDocs(TestDocsCommon1):

    def test_merge_document__same_docs(self):
        with self.assertRaises(ValidationError):
            self.doc_2.merge(self.doc_2)

    def test_merge_document__normal(self):
        # merge documents no lang, no tag
        self.assertEqual(self.doc_2.contents_count, 1)
        self.doc.merge(self.doc_2)
        doc = self.env['website.document'].browse(self.doc.id).exists()
        self.assertFalse(doc)
        # update contents count
        self.assertEqual(self.doc_2.contents_count, 2)

    def test_merge_document__with_lang(self):
        # merge documents with lang
        self.doc.lang_ids = [(6, 0, [self.lang_en.id])]
        self.doc_2.lang_ids = [(6, 0, [self.lang_vi.id])]
        self.assertEqual(self.doc_2.contents_count, 1)
        self.assertEqual(len(self.doc_2.lang_ids), 1)
        self.doc.merge(self.doc_2)
        doc = self.env['website.document'].browse(self.doc.id).exists()
        # source document have been removed
        self.assertFalse(doc)
        # update contents count
        self.assertEqual(self.doc_2.contents_count, 2)
        # update lang
        self.assertEqual(len(self.doc_2.lang_ids), 2)
        self.assertRecordValues(self.doc_2.lang_ids.sorted('id'), [{'id': self.lang_en.id}, {'id': self.lang_vi.id}])

    def test_merge_document__with_tag(self):
        # merge documents with tag
        self.doc.tag_ids = [(6, 0, [self.tag_1.id])]
        self.doc_2.tag_ids = [(6, 0, [self.tag_2.id, self.tag_3.id])]
        self.assertEqual(self.doc_2.contents_count, 1)
        self.assertEqual(len(self.doc_2.tag_ids), 2)
        self.doc.merge(self.doc_2)
        doc = self.env['website.document'].browse(self.doc.id).exists()
        # source document have been removed
        self.assertFalse(doc, 'Source document should be removed')
        # update contents count
        self.assertEqual(self.doc_2.contents_count, 2)
        # update tags
        self.assertEqual(len(self.doc_2.tag_ids), 3)
        self.assertRecordValues(self.doc_2.tag_ids.sorted('id'), [{'id': self.tag_1.id}, {'id': self.tag_2.id}, {'id': self.tag_3.id}])

    def test_merge_document__update_name(self):
        # check update name on merge wizard => update source doc name for dest doc
        self.assertEqual(self.doc_2.contents_count, 1)
        self.doc.with_context(update_dest_doc_name=True).merge(self.doc_2)
        doc = self.env['website.document'].browse(self.doc.id).exists()
        self.assertFalse(doc)
        # update contents count
        self.assertEqual(self.doc_2.contents_count, 2)
        # update doc name
        self.assertEqual(self.doc_2.name, 'Activate the Developer (Debug) Mode')
