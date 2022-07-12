{
    'name': "Odoo Apps Project Sales",
    'name_vi_VN': 'Tích hợp bán ứng dụng Odoo với Dự án',
    'summary': """
Sell project specific apps""",
    'summary_vi_VN': 'Tích hợp bán ứng dụng với dự án',
    'description': """
Sell your Odoo development/customization services and allow customer download the apps that were developed according to the ordered services

Key Features
============

1. Assign Odoo Apps to Project Tasks
2. Customer can download apps related to project tasks that have been invoiced and get paid.

    """,
    'description_vi_VN': """
    Bán các dịch vụ phát triển / tùy chỉnh Odoo của bạn và cho phép khách hàng tải xuống các ứng dụng được phát triển theo các dịch vụ được đặt hàng

Các tính năng chính
===================

1. Gán ứng dụng Odoo cho các nhiệm vụ dự án
2. Khách hàng có thể tải xuống các ứng dụng liên quan đến các nhiệm vụ dự án đã được lập hóa đơn và được thanh toán.

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Odoo Apps',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['to_odoo_module_sale', 'sale_timesheet', 'to_git_project'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'views/odoo_module_version_views.xml',
        'views/project_task_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
