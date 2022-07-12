from odoo.tests import tagged
from odoo.tests.common import Form

from .common import Common


@tagged('post_install', '-at_install')
class TestShareHolder(Common):

    #Case 1
    def test_create_new_contact(self):
        """
        INPUT: Tạo mới 1 liên hệ, thêm thông tin cổ đông cho liên hệ
        OUTPUT: Thông tin cổ đông được gắn với liên hệ
        """
        self.assertEqual(self.contact_a.shareholder_ids.id, self.share_holder.id)
        
    #Case 2
    def test_onchange_type_company(self):        
        """
        INPUT: Thay đổi kiểu công ty của liên hệ từ công ty sang cá nhân
        OUTPUT: Thông tin cổ đông sẽ biến mất
        """
        contact_a_form = Form(self.contact_a)
        contact_a_form.company_type = 'person'
        self.assertFalse(contact_a_form.shareholder_ids)
