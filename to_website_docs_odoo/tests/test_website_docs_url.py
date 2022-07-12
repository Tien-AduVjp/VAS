from lxml import etree

from odoo.tests import HttpCase, tagged

from .common2 import TestDocsCommon2


@tagged('post_install', '-at_install', 'external')
class TestWebsiteDocsUrl(TestDocsCommon2, HttpCase):

    def test_website_url(self):
        # docs content
        # normal url
        content_url = self.doc_content_3.get_website_url()
        content_url_resp = self.url_open(content_url)
        self.assertEqual(content_url_resp.status_code, 200)
        # no version
        content_url_no_version = self.doc_content_4.get_website_url()
        content_url_no_version_resp = self.url_open(content_url_no_version)
        self.assertEqual(content_url_no_version_resp.status_code, 200)
        # change document_type to hash
        self.category_general.document_type = 'hash'
        self.category_general.flush(['document_type'])
        # with hash
        content_url_with_hash = self.doc_content_4.get_website_url()
        content_url_with_hash_resp = self.url_open(content_url_with_hash)
        self.assertEqual(content_url_with_hash_resp.status_code, 200)

        # document
        # with hash
        doc_url_hash = self.doc.get_website_url()
        doc_url_hash_resp = self.url_open(doc_url_hash)
        self.assertEqual(doc_url_hash_resp.status_code, 200)
        # normal url
        doc_url = self.doc_2.get_website_url()
        doc_url_resp = self.url_open(doc_url)
        self.assertEqual(doc_url_resp.status_code, 200)
        # no version
        doc_url_no_version = self.doc_3.get_website_url()
        doc_url_no_version_resp = self.url_open(doc_url_no_version)
        self.assertEqual(doc_url_no_version_resp.status_code, 200)

        # category
        # normal url
        cat_url = self.category_general.get_website_url()
        cat_url_resp = self.url_open(cat_url)
        self.assertEqual(cat_url_resp.status_code, 200)

    def test_docs_search_with_odoo_version(self):
        content = self.doc_content_2
        content.document_id.state = 'approved'
        content.state = 'approved'
        content.action_publish_toggle()
        version_id = content.odoo_version_id.id
        # Case: search keyword is in existing content, odoo version exist => Found
        resp = self.url_open(self.base_url + "/docs/search?search=%s&version=%s" % ('Angular', version_id))
        root = etree.fromstring(resp.content, etree.HTMLParser())
        tag = root.xpath("//div[contains(@class, 'docs-info')]")
        self.assertTrue(tag)
        # Case: search with the non-existent version => Notfound
        version_id = 100
        resp = self.url_open(self.base_url + "/docs/search?search=%s&version=%s" % ('Angular', version_id))
        root = etree.fromstring(resp.content, etree.HTMLParser())
        tag = root.xpath("//div[contains(@class, 'docs-info')]")
        self.assertFalse(tag)
