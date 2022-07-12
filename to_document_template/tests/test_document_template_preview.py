from odoo.tests.common import Form, tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestDocumentTemplatePreview(Common):
    
    def setUp(self):
        super(TestDocumentTemplatePreview, self).setUp()
        DocumentTemplatePreview = self.env['document_template.preview'].with_context(template_id=self.document_template.id)
        self.document_template_preview = Form(DocumentTemplatePreview)

    def test_onchange_res_id(self):
        """
        Kiểm tra thay đổi trên Document Template Preview:
        - Input: Tạo hoặc chọn một document template
        - Output: Click vào Preview, hiển thị popup preview với Content đã tạo ở document template
        """
        self.assertEqual(self.document_template_preview.content_html, self.document_template.content_html)
