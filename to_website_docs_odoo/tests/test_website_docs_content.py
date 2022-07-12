from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger
from .common import TestDocsCommon


@tagged('post_install', '-at_install')
class TestWebsiteDocsContent(TestDocsCommon):

    def test_sql_constraint_uniq_odoo_version_doc_content(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            # cannot create document content with same version in same doc
            DocumentContent = self.env['website.document.content']
            doc_content = DocumentContent.search([('document_id', '=', self.doc_2.id), ('odoo_version_id', '=', self.odoo_version_v20.id)])
            self.assertTrue(doc_content)
            DocumentContent.create({
                'document_id': self.doc_2.id,
                'odoo_version_id': self.odoo_version_v20.id
            })

    def test_func_get_other_odoo_versions(self):
        # get all versions other than current content (content unpublished)
        unpublished = self.doc_content_2.get_other_odoo_versions(False)
        self.assertEqual(unpublished[0].name, '21.0')
        self.doc_content_4.write({
            'document_id': self.doc_2.id,
            'odoo_version_id': self.odoo_version_v22
        })
        # get all versions other than current content (content published)
        published = self.doc_content_2.get_other_odoo_versions(True)
        self.assertEqual(published[0].name, '22.0')
