from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestHrDepartment(Common):   
       
    #Case 1
    def test_create_new_deparment(self):
        """
        INPUT: Tạo  mới 1 phòng ban có tên là department_test
        OUPUT: Một tài khoản kế toán quản trị có tên là department_test được sinh ra. 
               Tài khoản này liên kết với phòng ban department_test và có công ty trùng với công ty của phòng ban
        """
        department = self.create_hr_department('department_test')        
        self.assertRecordValues(
            department.analytic_account_id,
            [
                {
                    'name': 'department_test',
                    'company_id': department.company_id.id,
                }
            ]
        )
    
    #Case 2
    def test_create_new_analytic_tag_1(self):
        """
        INPUT: Tạo mới 1 thẻ quản trị, tích vào phân bổ KT quản trị, thêm 2 phòng ban gắn với thẻ quản trị này
        OUTPUT: Gợi ý, phân bổ doanh thu cho mỗi phòng ban là 50%
        """
        departments = self.department_management | self.department_research_development
        analytic_tag = self.create_analytic_tag(departments)    
        self.assertEqual(set(analytic_tag.analytic_distribution_ids.mapped('percentage')), {50})
    
    #Case 3
    def test_create_new_analytic_tag_2(self):
        """
        INPUT: Tạo mới 1 thẻ quản trị, tích vào phân bổ KT quản trị, thêm 1 phòng ban gắn với thẻ quản trị này
        OUTPUT: Phòng ban sẽ liên kết với thẻ quản trị được tạo. Khi vào chi tiết của phòng ban, ở phần thẻ quản trị
                sẽ thấy thẻ quản trị được tạo
        """
        analytic_tag = self.create_analytic_tag(self.department_management)        
        self.assertEqual(analytic_tag.id, analytic_tag.department_ids.analytic_tag_ids.id)
