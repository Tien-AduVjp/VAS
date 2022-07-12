from odoo.tests.common import Form, tagged

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):
    #Case 1
    def test_access_right_user_full_accounting_feature(self):  
        """
        INPUT: 
            Tích cho user các quyền:
                - Kế toán viên
                - Kế toán quản trị
                - Thẻ tài khoản quản trị
            Mở form tạo mới 1 phòng ban.
               
        OUTPUT: 
            Trên form xuất hiện các cài đặt kế toán cho phòng ban:
                - Tài khoản chi phí
                - Tài khoản kế toán quản trị
                - Thẻ tài khoản quản trị        
        """      
        self.department_form = Form(self.env['hr.department'].with_user(self.user_full_accounting_feature))        
        self.assertFalse(self.department_form._get_modifier('account_expense_id', 'invisible'))
        self.assertFalse(self.department_form._get_modifier('analytic_account_id', 'invisible'))
        self.assertFalse(self.department_form._get_modifier('analytic_tag_ids', 'invisible'))
        
    #Case 2
    def test_access_right_user_analytic_accounting(self):       
        """
        INPUT: 
            Tích cho user các quyền:
                - Kế toán viên
                - Kế toán quản trị
            Mở form tạo mới 1 phòng ban, 
            
        OUTPUT: 
            Trên form xuất hiện các cài đặt kế toán cho phòng ban:
                - Tài khoản chi phí
                - Tài khoản kế toán quản trị      
        """   
        self.department_form = Form(self.env['hr.department'].with_user(self.user_analytic_accounting))        
        self.assertFalse(self.department_form._get_modifier('account_expense_id', 'invisible'))
        self.assertFalse(self.department_form._get_modifier('analytic_account_id', 'invisible'))
        self.assertTrue(self.department_form._get_modifier('analytic_tag_ids', 'invisible'))
        
    #Case 3
    def test_access_right_user_analytic_accounting_tags(self):      
        """
        INPUT: 
            Tích cho user các quyền:
                - Kế toán viên
                - Thẻ tài khoản quản trị
            Mở form tạo mới 1 phòng ban, 
        OUTPUT: 
            Trên form xuất hiện các cài đặt kế toán cho phòng ban:
                - Tài khoản chi phí
                - Thẻ tài khoản quản trị        
        """    
        self.department_form = Form(self.env['hr.department'].with_user(self.user_analytic_accounting_tags))        
        self.assertFalse(self.department_form._get_modifier('account_expense_id', 'invisible'))
        self.assertTrue(self.department_form._get_modifier('analytic_account_id', 'invisible'))
        self.assertFalse(self.department_form._get_modifier('analytic_tag_ids', 'invisible'))       
