from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    
    def setUp(self):
        super(Common, self).setUp()
        self.model_id = self.env.ref('to_document_template.model_document_template')
        self.model_object_field1 = self.env.ref('to_document_template.field_document_template__name')
        self.model_object_field2 = self.env.ref('to_document_template.field_document_template__model_id')
        self.sub_model_object_field = self.env.ref('base.field_ir_model__name')
        self.null_value = 'Demo'
        self.document_template = self.env['document.template'].create({
            'name': 'Demo', 
            'model_id': self.model_id.id,
            'content_html': '<p>Demo</p>'
        })
        self.internal_user = self.env.ref('base.user_demo') 
        self.settings_user = self.env.ref('base.user_admin')
