{
    'name': 'HR Meal Order & Payroll Integration',
    'name_vi_VN': "Tích hợp Đặt suất ăn và Bảng lương",
    'category': 'Human Resources/Payroll',
    'version': '0.1.1',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'maintainer': 'T.V.T Marine Automation (aka TVTMA)',
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'summary': """
Deduct Meal Order price in Employee Payslip""",
    'summary_vi_VN': """
Khấu trừ tiền đặt suất ăn vào phiếu lương nhân viên """,

    'description': """
What it does
============

This application provide integration between the HR Meal application and HR Payroll application to deduct Meal Order price in Employee Payslip.

Key Features
============

#. HR Meal

   * Displays the price that employee has to pay for the meal and calculates the difference between the company's pay and employee's pay.

#. Payslip

   * When the "Compute Sheet" button, Odoo will search for all meal order line of employee for a period of time and add them to the payslip so that salary rules can access it with the dot syntax **payslip.meal_order_line_ids**.
   * When the "Confirm" button is hit, Odoo will "Compute Sheet" before doing confirmation.

#. Salary Rules Access

   * **result = -1 * sum(payslip.meal_order_line_ids.mapped('emp_total_price'))** will summarize all the meal order line and return the result for the salary rule
   * etc.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

Ứng dụng này cung cấp tích hợp giữa ứng dụng HR Meal và ứng dụng HR Payroll để khấu trừ giá đặt suất ăn vào phiếu lương của nhân viên.

Các tính năng chính
===================

#. Đặt suất ăn

   * Hiển thị giá nhân viên phải trả cho bữa ăn và tính toán sự chênh lệnh giữa giá phải trả của công ty và giá phải trả của nhân viên.

#. Phiếu Lương

   * Khi bấm nút "Bảng tính toán", Odoo sẽ tìm kiếm tất cả các lệnh đặt suất ăn của nhân viên đó trong một khoảng thời gian và thêm chúng vào phiếu lương để quy tắc lương có thể truy cập bằng cú pháp dấu chấm **paylip.meal_order_line_ids**.
   * Khi nhấn nút "Xác nhận", Odoo sẽ chạy "Bảng tính toán" trước khi thực hiện xác nhận.

#. Truy cập quy tắc lương

   * **result = sum(payslip.hr_expense_ids.mapped(total_amount))** sẽ tổng hợp tất cả các dòng đặt suất ăn và trả lại kết quả cho quy tắc lương.
   * v.v.

Phiên bản được hỗ trợ
=====================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'depends': ['to_hr_payroll', 'to_hr_meal'],
    'data': [
        'data/hr_contribution_category_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/res_config_setting_view.xml',
        'views/meal_order_line_views.xml',
        'views/meal_order_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'post_init_hook': 'post_init_hook',
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
