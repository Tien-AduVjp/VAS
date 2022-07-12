{
    'name': "Viin Fleet",
    'name_vi_VN': "Đội Phương tiện Cơ sở",
    'summary': """
Technical module that improves Fleet application at technical aspects""",
    'summary_vi_VN': """
Module kỹ thuật để cải tiến các khía cạnh kỹ thuật của ứng dụng Đội Phương tiện""",

    'description': """
Key Features
============
#. Allow to record Price Unit and Quantity when logging vehicle services.
#. Improve the Vehicle Cost Report: add criteria on Vendor, Service Type, Quantity and Price Unit.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============
#. Cho phép nhập Đơn giá và Số lượng khi ghi nhận dịch vụ cho phương tiện.
#. Cải tiến Báo cáo Chi phí Phương tiện: Bổ sung tiêu chí theo Nhà cung cấp, Kiểu Dịch vụ, Số lượng và Đơn giá.

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['fleet'],

    # always loaded
    'data': [
        'security/fleet_security.xml',
        'security/ir.model.access.csv',
        'views/fleet_vehicle_log_service_views.xml',
        'reports/fleet_vehicle_cost_report_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['fleet'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
