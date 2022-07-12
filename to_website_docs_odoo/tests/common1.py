from odoo import fields
from odoo.addons.to_website_docs.tests.common1 import TestDocsCommon1


class TestDocsCommon1(TestDocsCommon1):

    @classmethod
    def setUpClass(cls):
        super(TestDocsCommon1, cls).setUpClass()

        Document = cls.env['website.document']
        Content = cls.env['website.document.content']
        OdooVersion = cls.env['odoo.version']
        cls.doc_3 = Document.create({
            'name': 'Document No Content',
            'category_id': cls.category_general_3.id
        })
        cls.doc_4 = Document.create({
            'name': 'Python docs',
            'category_id': cls.category_general_2.id
        })
        cls.odoo_version_v20 = OdooVersion.create({
            'name': '20.0',
            'release_date': fields.Date.from_string('2021-5-5'),
        })
        cls.odoo_version_v21 = OdooVersion.create({
            'name': '21.0',
            'release_date': fields.Date.from_string('2021-7-8'),
        })
        cls.odoo_version_v22 = OdooVersion.create({
            'name': '22.0',
            'release_date': fields.Date.from_string('2021-7-9')
        })
        cls.doc_content_2.odoo_version_id = cls.odoo_version_v20.id

        cls.doc_content_3 = Content.create({
            'document_id': cls.doc_2.id,
            'odoo_version_id': cls.odoo_version_v21.id,
            'fulltext': 'Introduction to the Angular Docs v21',
        })
        cls.doc_content_4 = Content.create({
            'document_id': cls.doc.id,
            'fulltext': 'Introduction to the Nodejs Docs',
            'state': 'approved',
            'is_published': True
        })
        cls.doc_content_5 = Content.create({
            'document_id': cls.doc_4.id,
            'odoo_version_id': cls.odoo_version_v22.id,
            'fulltext': 'Introduction to the Python Docs',
            'state': 'approved'
        })
