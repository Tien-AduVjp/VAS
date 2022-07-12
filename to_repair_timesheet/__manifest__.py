{
    'name': 'Repair Timesheet',
    'name_vi_VN': 'Chấm công sửa chữa',

    'summary': """
Integrate Timesheet application with Repair application
        """,

    'summary_vi_VN': """
Tích hợp chấm công cho dịch vụ sửa chữa.
        """,

    'description': """
What it does
============
This module helps integrate Timesheet application with Repair application:

* Repair service linked with tasks helps enable tasks log and invoicing based on timesheets
* Allow to create many invoices (by milestones, by service scope, etc.) for one repair order

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

Mô-đun này giúp tích hợp ứng dụng Chấm công với ứng dụng Sửa chữa:

* Các dịch vụ sửa chữa sẽ được gắn với các nhiệm vụ, giúp người dùng có thể chấm công và xuất hóa đơn theo công việc đã thực hiện thực tế.
* Cho phép xuất nhiều hóa đơn (có thể theo từng giai đoạn, hạng mục hoàn thành v.v) cho một đơn sửa chữa.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'category': 'Operations/Timesheets',
    'author': "Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'depends': ['sale_timesheet', 'to_repair_supply'],
    'data': [
        'wizard/repair_make_invoice_advance_views.xml',
        'views/repair_views.xml',
        'report/repair_templates_repair_order.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
