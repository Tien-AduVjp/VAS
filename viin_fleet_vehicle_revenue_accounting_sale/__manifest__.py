{
    'name': "Fleet Vehicle Revenue Accounting - Sale",
    'name_vi_VN': "Kế toán Doanh thu Đội phương tiện - Sale",

    'summary': """
Fleet Vehicle Revenue, Accounting, Sale
    """,
    'summary_vi_VN': """
Doanh thu Đội phương tiện, Kế toán, Bán
    """,

    'description': """
What it does
============
* Bridge between Fleet Vehicle Revenue Accounting and Sale
* Generate access right to Fleet Vehicle Revenue Accounting for Salesman

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Mô đun cầu nối giữa Kế toán Doanh thu Đội phương tiện và Bán hàng
* Phân quyền đọc dữ liệu Doanh thu Đội phương tiện cho Nhân viên Bán hàng

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Accounting & Finance',
    'version': '0.1.0',
    'depends': ['to_fleet_vehicle_revenue_accounting', 'sale'],

    'data': [
        'security/module_security.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False, # mark this as True after upgrading for Odoo 14
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
