from odoo.tests.common import Form, tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestDocumentTemplate(Common):
    
    def test_onchange_sub_model_object_value_field(self):
        """
        Kiểm tra khi thay đổi trường trên model Document Template:
        TH1:
        - Input: Chọn hoặc tạo mới document template
            Tên:  Demo, 
            Model áp dụng : Mẫu tài liệu (document.template), 
            Trường áp dụng: name (là một trường không quan hệ),
            Giá trị mặc định : Demo
        - Output:
            Tên:  Demo, 
            Model áp dụng : Mẫu tài liệu (document.template), 
            Trường áp dụng: name (là một trường không quan hệ),
            Giá trị mặc định : Demo
            Biểu thức Placeholder: ${object.name or '''Demo'''}
        TH2:
        - Input:
            Tên:  Demo, 
            Model áp dụng : Mẫu tài liệu (document.template), 
            Trường áp dụng: model_id (là một trường quan hệ),
            Trường thứ cấp: name
            Giá trị mặc định : Demo
        - Output:
            Tên:  Demo, 
            Model áp dụng : Mẫu tài liệu (document.template), 
            Trường áp dụng: model_id (là một trường quan hệ),
            Trường thứ cấp: name
            Giá trị mặc định : Demo
            Biểu thức Placeholder: ${object.model_id.name or '''Demo'''}
        """
        document_template_form = Form(self.env['document.template'])
        document_template_form.name = 'Demo'
        document_template_form.model_id = self.model_id
        document_template_form.model_object_field = self.model_object_field1
        document_template_form.null_value = self.null_value

        #TH1: Create a document template with non-relational field 'model_object_field'
        document_template1 = document_template_form.save()
        self.assertEqual(document_template1.copyvalue, "${object.name or '''Demo'''}")
        
        #TH2: Create a document template with relational field 'model_object_field'
        document_template_form.model_object_field = self.model_object_field2
        document_template_form.sub_model_object_field = self.sub_model_object_field
        document_template2 = document_template_form.save()
        self.assertEqual(document_template2.copyvalue, "${object.model_id.name or '''Demo'''}")
    
    def test_function_build_expression(self):
        """
        Kiểm tra hàm build_expression(self, field_name, sub_field_name, null_value):
        - Input:
            + TH1: field_name = 'model_id' , sub_field_name = 'name', null_value = 'Demo'
            + TH2: field_name = 'model_id' , sub_field_name = False, null_value = 'Demo' 
            + TH3: field_name = 'model_id' , sub_field_name = False, null_value = 'False' 
            + TH4: field_name = False , sub_field_name = 'name', null_value = 'Demo'
        - Output:
            + TH1: ${object.model_id.name or '''Demo'''}
            + TH2: ${object.model_id or '''Demo'''}
            + TH3: ${object.model_id}        
            + TH4: giá trị rỗng
        """
        # field_name = 'model_id' , sub_field_name = 'name', null_value = 'Demo'
        result1 = self.env['document.template'].build_expression('model_id', 'name', 'Demo')
        self.assertEqual(result1, "${object.model_id.name or '''Demo'''}")

        # field_name = 'model_id' , sub_field_name = False, null_value = 'Demo'
        result2 = self.env['document.template'].build_expression('model_id', False, 'Demo')
        self.assertEqual(result2, "${object.model_id or '''Demo'''}")

        # field_name = 'model_id' , sub_field_name = False, null_value = 'False'
        result3 = self.env['document.template'].build_expression('model_id', False, False)
        self.assertEqual(result3, "${object.model_id}")
        
        # field_name = False , sub_field_name = 'name', null_value = 'Demo'
        result4 = self.env['document.template'].build_expression(False, 'name', 'Demo')
        self.assertEqual(result4, '')
