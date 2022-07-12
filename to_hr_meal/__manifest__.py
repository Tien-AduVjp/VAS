# -*- coding: utf-8 -*-
{
    'name': "Meal Orders",
    'name_vi_VN': "Suất ăn",

    'summary': """Manage Meal Orders for your employees""",
    'summary_vi_VN': """Quản lý đơn đặt hàng bữa ăn cho nhân viên của bạn""",

    'description': """

What it does
============
This module helps you manage mass meals orders for your employees which will be sent to the company's kitchens. It also let you know in details the cost of the meals for your employees over the time

Key Features
============
* Meal Users can create a meal order for multiple employee at once for a time of a day (Lunch, Dinner, Night Meal for Night workers, etc)
* Meal users can also order meals for the company's guess which will bind to the employee who is in charge of the guess
* Once confirmed, the person in charge of the kitchen will get notified about the order so that she or he can approve/refuse the order
* Meal Managers can define unlimited meal types which will be used in the meal orders for categorizing meals.
* Meal Manager can define a standard price for each meal type for cost concerning purposes
* Meal Manager can define unlimited meal alerts for usage in meal type, which aim to alert Meal Users for the time to order meals. For example, Lunch must be ordered before 10:00 AM.
* Support multiple kitchens for large companies

Reports & Analysis
------------------
* Analyze meals by

    * Employee
    * Department
    * Kitchen
    * Date Ordered (Date / Week / Month / Year)
    * Date Approved (Date / Week / Month / Year)
    * Ordered by (the one who placed the meal order)
    * Order
    * Meal Type
    * Order Status
    
* Measurement

    * Meal Quantity
    * Meal Order Count
    * Price
    * Total Price
    
* Report types

    * Pivot
    * Graph

Each meal order consists 
Meal Users: can request for a meal order, in which

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả 
=====
Mô-đun này giúp bạn quản lý lệnh đặt suất ăn của nhân viên trên số lượng lớn, và gửi các đơn đặt này tới nhà bếp của công ty. Mô-đun này cũng cho phép bạn nắm được chi tiết chi phí bữa ăn cho nhân viên theo thời gian. 

Tính năng nổi bật
=================
* Người đặt suất ăn có thể tạo lệnh đặt suất ăn cho nhiều nhân viên cùng lúc cho từng bữa nhất định (ví dụ bữa trưa, bữa tối, bữa khuya cho nhân viên làm đêm, v.v) 
* Người đặt suất ăn cũng có thể đặt cho cả khách của công ty, và chi phí suất ăn đó sẽ được tính vào chi phí của nhân viên phụ trách khách hàng này 
* Sau khi xác nhận, người phụ trách nhà bếp sẽ nhận được thông báo về lệnh đặt, và có thể xác nhận hoặc từ chối đơn đó. 
* Người quản lý bữa ăn có thể tạo nhiều kiểu suất ăn khác nhau, dùng để phân loại suất ăn trong lệnh đặt 
* Người quản lý bữa ăn có thể đặt giá tiêu chuẩn cho từng loại bữa ăn, phục vụ cho các mục đích liên quan đến chi phí 
* Người quản lý bữa ăn có thể tạo thông báo cho các bữa ăn, nhằm lưu ý cho người đặt về thời gian đặt bữa. Ví dụ, bữa trưa phải được đặt hoàn tất trước 10h sáng. 
* Hỗ trợ việc quản lý nhiều bếp ăn cho các công ty lớn

Báo cáo & Phân tích
-------------------
* Phân tích bữa ăn theo:

   * Nhân viên 
   * Phòng ban 
   * Bếp ăn 
   * Ngày đặt (Ngày/ Tuần/ Tháng/ Năm)
   * Ngày xác nhận lệnh (Ngày/ Tuần/ Tháng/ Năm) 
   * lệnh đặt 
   * Loại suất ăn 
   * Tình trạng đặt 

* Đo lường

   * Số lượng suất ăn 
   * Số lượng lệnh đặt 
   * Giá từng suất ăn
   * Tổng giá các suất ăn

* Các loại báo cáo 

   * Dạng bảng cột 
   * Dạng đồ thị 

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com/intro/hr-meal",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources/Meal',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_holidays', 'to_base'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'data/kitchen_data.xml',
        'data/meal_type_data.xml',
        'security/meal_security.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/kitchen_views.xml',
        'views/meal_type_alert_views.xml',
        'views/meal_type_views.xml',
        'views/meal_order_views.xml',
        'views/meal_order_line_views.xml',
        'views/meal_orders_analysis.xml',
        'views/hr_employee_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 119,
    'price': 45.9,
    'subscription_price': 3.31,
    'currency': 'EUR',
    'license': 'OPL-1',
}
