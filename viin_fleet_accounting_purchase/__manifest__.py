{
    'name': "Fleet Accounting - Purchase",
    'name_vi_VN': "Kế toán Đội phương tiện - Mua",

    'summary': """
Fleet, Accounting, Purchase
    """,
    'summary_vi_VN': """
Đội phương tiện, Kế toán, Mua
    """,

    'description': """
What it does
============
Bridge between Fleet Accounting and Purchase
* Generate access right to Fleet Vehicle Cost for Purchase User

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô đun cầu nối giữa Kế toán Đội phương tiện và Mua
* Phân quyền đọc dữ liệu Chi phí Đội phương tiện cho Người dùng Mua hàng

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
    'depends': ['to_fleet_accounting', 'purchase'],

    'data': [
        'security/module_security.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False, # mark this as True after upgrading for Odoo 14
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
