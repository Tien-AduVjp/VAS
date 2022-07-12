{
    'name': "Fleet Operation Revenue Accounting",
    'name_vi_VN': "Kế Toán Doanh Thu Hoạt Động Đội Phương Tiện",
    'summary': """
Fleet Operation Revenue with Accounting integration""",
    'summary_vi_VN': """
Tích hợp Doanh Thu Hoạt Động Đội Phương Tiện với Kế Toán""",
    'description': """
Integrate the module 'Fleet Operation Accounting' and the module 'Fleet Revenue Accounting' to manage vehicle trips' revenue in Accounting

Key Features
============
1. Manage vehicle trips' revenue in accounting
2. Invoice customers according to the revenue of the trips (generate customer invoices from trips)
3. Allocate customer invoices to existing trips for trip and vehicle revenue analysis
4. Analyse your trips revenue with accounting
5. Analyse your trips revenue with analytics accounting

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tích hợp mô-đun 'Kế Toán Hoạt Động Đội Phương Tiện' và mô-đun 'Kế Toán Doanh Thu Đội Phương Tiện' để quản lý doanh thu các chuyến đi của phương tiện trong Kế toán.

Tính năng chính
===============
1. Quản lý doanh thu các chuyến đi của phương tiện trong kế toán
2. Hóa đơn cho khách hàng theo doanh thu của các chuyến đi (tạo hóa đơn của khách hàng từ các chuyến đi)
3. Phân bổ các hóa đơn của khách hàng đến các chuyến đi hiện tại để phân tích doanh thu chuyến đi và phương tiện
4. Phân tích doanh thu các chuyến đi của bạn với kế toán
5. Phân tích doanh thu các chuyến đi của bạn với kế toán phân tích

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Fleet Transportation',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_fleet_vehicle_revenue_accounting', 'to_fleet_accounting_fleet_operation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_revenue_views.xml',
        'wizard/vehicle_trip_register_revenue_wizard_views.xml',
        'wizard/trip_invoicing_revenue_wizard_views.xml',
        'wizard/vehicle_revenue_allocation_wizard_views.xml',
        'views/fleet_vehicle_trip_views.xml',
        'views/trip_analysis.xml',
        'views/fleet_vehicle_revenue_report.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False,  # set as True while upgrading to 14
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
