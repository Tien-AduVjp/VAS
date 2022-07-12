from datetime import date

from odoo.tests.common import tagged, Form

from .common import Common


@tagged('-at_install', 'post_install')
class TestMealOrder(Common):
    
    def test_01_check_meal_order(self):
        """
        Case 1: Kiểm tra tổng số tiền nhân viên phải trả và công ty phải trả
        - Input: 
            + Hợp đồng ở trạng thái New chưa chạy lần nào, trên hợp đồng nhân viên có thiết lập số tiền cho mỗi bữa ăn là 30000 đồng
            + Đơn đặt bữa ăn có kiểu là ăn trưa cho tất cả mọi người
            + Dòng đặt bữa ăn của nhân viên, giá 35000 đồng, số lượng 1
        - Output:
            + Tổng tiền phải trả của nhân viên là 0
            + Tổng tiền phải trả của công ty là 35000
            + Giá nhân viên trên dòng đặt hàng là 0
        """
        self.contract_employee_demo.write({'pay_per_meal': 30000})
        meal_line_data = {
            'employee_id': self.employee_demo.id,
            'quantity': 1,
            'price': 35000,
            'meal_type_id': self.meal_type_1.id
        }
        self.meal_order_1.write({'order_line_ids': [(0, 0, meal_line_data)]})
        self.assertEqual(self.meal_order_1.total_employee_pay, 0)
        self.assertEqual(self.meal_order_1.total_company_pay, 35000)
        self.assertEqual(set(self.meal_order_1.order_line_ids.mapped('employee_price')), {0})
    
    def test_02_check_meal_order(self):
        """
        Case 2: Kiểm tra tổng số tiền nhân viên phải trả và công ty phải trả
        - Input: 
            + Hợp đồng ở trạng thái đang mở hoặc đã từng mở, trên hợp đồng nhân viên có thiết lập số tiền cho mỗi bữa ăn là 30000 đồng
            + Đơn đặt bữa ăn có kiểu là ăn trưa cho tất cả mọi người
            + Dòng đặt bữa ăn của nhân viên, giá 35000 đồng, số lượng 1
        - Output: 
            + Tổng tiền phải trả của nhân viên là 30000
            + Tổng tiền phải trả của công ty là 5000
            + Giá nhân viên trên dòng đặt hàng là 30000
        """
        self.contract_employee_demo.write({'pay_per_meal': 30000, 'state': 'open'})
        meal_line_data = {
            'employee_id': self.employee_demo.id,
            'quantity': 1,
            'price': 35000,
            'meal_type_id': self.meal_type_1.id
        }
        self.meal_order_1.write({'order_line_ids': [(0, 0, meal_line_data)]})
        self.assertEqual(self.meal_order_1.total_employee_pay, 30000)
        self.assertEqual(self.meal_order_1.total_company_pay, 5000)
        self.assertEqual(set(self.meal_order_1.order_line_ids.mapped('employee_price')), {30000})
    
    def test_03_check_meal_order(self):
        """
        Case 3: Kiểm tra tổng số tiền nhân viên phải trả và công ty phải trả
        - Input: 
            + Hợp đồng nhân viên không thiết lập giá bữa ăn, Thiết lập giá bữa ăn mặc định của công ty là 30000
            + Đơn đặt bữa ăn có kiểu là ăn trưa cho tất cả mọi người
            + Dòng đặt bữa ăn của nhân viên, giá 35000 đồng, số lượng 1
        - Output: 
            + Tổng tiền phải trả của nhân viên là 30000
            + Tổng tiền phải trả của công ty là 5000
            + Giá nhân viên trên dòng đặt hàng là 30000
        """
        self.env.company.write({'default_meal_emp_price': 30000})
        meal_line_data = {
            'employee_id': self.employee_demo.id,
            'quantity': 1,
            'price': 35000,
            'meal_type_id': self.meal_type_1.id
        }
        self.meal_order_1.write({'order_line_ids': [(0, 0, meal_line_data)]})
        self.assertEqual(self.meal_order_1.total_employee_pay, 30000)
        self.assertEqual(self.meal_order_1.total_company_pay, 5000)
        self.assertEqual(set(self.meal_order_1.order_line_ids.mapped('employee_price')), {30000})
    
    def test_04_check_meal_order(self):
        """
        Case 4: Kiểm tra số tiền nhân viên phải trả cho mỗi suất ăn với tính năng tạo suất ăn hàng loạt
        - Input: 
            + Hợp đồng nhân viên 1 thiết lập giá bữa ăn 30000, Thiết lập giá bữa ăn mặc định của công ty là 40000
            + Đơn đặt bữa ăn có kiểu là ăn trưa cho tất cả mọi người, tạo hàng loạt cho tất cả nhân viên
        - Output: 
            + Giá nhân viên 1 phải trả là 30000
        """
        self.env.company.write({'default_meal_emp_price': 40000})
        meal_order_form = Form(self.env['hr.meal.order'])
        meal_order_form.meal_type_id = self.meal_type_1
        meal_order_form.load_employee = 'load_all'
        meal_order = meal_order_form.save()
        meal_of_employee = meal_order.order_line_ids.filtered(lambda m: m.employee_id == self.employee_1)
        self.assertEqual(meal_of_employee.employee_price, 30000)
