# -*- coding: utf-8 -*-
{
    'name': "Fleet Operation Accounting",
    'name_vi_VN': "Kế Toán Hoạt Động Đội Phương Tiện",
    'summary': """
Integrate the module 'Fleet Operation & Planning' and the module Fleet Accounting""",
    'summary_vi_VN': 'Tích hợp mô-đun Hoạch định Hoạt động Đội phương tiện và mô-đun Kế Toán Đội Phương Tiện',
    'description': """
Integrate the module 'Fleet Operation & Planning' and the module Fleet Accounting to declare costs of vehicle trips and manage vendor bills associated with such the cost

Key Features
============
1. Manage vehicle trips' costs in accounting
2. Manage Vendor bills related to your vehicle trips (generate vendor bills from trips)
3. Allocate vendor bills to existing trips
4. Analyse your trips costs with accounting
5. Analyse your trips costs with analytics accounting

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tích hợp mô-đun 'Hoạch định Hoạt động Đội phương tiện' và mô-đun Kế Toán Đội Phương Tiện để kê khai chi phí của các chuyến và quản lý các hóa đơn của nhà cung cấp liên quan đến chi phí đó

Các tính năng chính
===================

1. Quản lý chi phí của các chuyến trong kế toán
2. Quản lý hóa đơn của nhà cung cấp liên quan đến các chuyến của bạn (tạo hóa đơn của nhà cung cấp từ các chuyến)
3. Phân bổ hóa đơn của nhà cung cấp cho các chuyến hiện có
4. Phân tích chi phí của các chuyến của bạn với kế toán
5. Phân tích chi phí của các chuyến của bạn với kế toán quản trị

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Fleet Transportation',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_fleet_operation_planning', 'to_fleet_accounting'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/vehicle_trip_register_cost_wizard_views.xml',
        'wizard/trip_invoicing_cost_wizard_views.xml',
        'wizard/vehicle_cost_allocation_wizard_views.xml',
        'views/fleet_vehicle_trip_views.xml',
        'views/fleet_vehicle_cost_report.xml',
        'views/fleet_vehicle_cost_views.xml',
        'views/account_analytic_line_views.xml',
        'views/account_move_line_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
