from odoo import fields
from odoo.addons.to_website_docs.tests.common2 import TestDocsCommon2


class TestDocsCommon2(TestDocsCommon2):

    def setUp(self):
        super(TestDocsCommon2, self).setUp()

        Document = self.env['website.document']
        Content = self.env['website.document.content']
        OdooVersion = self.env['odoo.version']
        self.doc_3 = Document.create({
            'name': 'Document No Content',
            'category_id': self.category_general_3.id
        })
        self.doc_4 = Document.create({
            'name': 'Python docs',
            'category_id': self.category_general_2.id
        })
        self.odoo_version_v20 = OdooVersion.create({
            'name': '20.0',
            'release_date': fields.Date.from_string('2021-5-5'),
        })
        self.odoo_version_v21 = OdooVersion.create({
            'name': '21.0',
            'release_date': fields.Date.from_string('2021-7-8'),
        })
        self.odoo_version_v22 = OdooVersion.create({
            'name': '22.0',
            'release_date': fields.Date.from_string('2021-7-9')
        })
        self.doc_content_2.odoo_version_id = self.odoo_version_v20.id

        self.doc_content_3 = Content.create({
            'document_id': self.doc_2.id,
            'odoo_version_id': self.odoo_version_v21.id,
            'fulltext': 'Introduction to the Angular Docs v21',
        })
        self.doc_content_4 = Content.create({
            'document_id': self.doc.id,
            'fulltext': 'Introduction to the Nodejs Docs',
            'state': 'approved',
            'is_published': True
        })
        self.doc_content_5 = Content.create({
            'document_id': self.doc_4.id,
            'odoo_version_id': self.odoo_version_v22.id,
            'fulltext': 'Introduction to the Python Docs',
            'state': 'approved'
        })
