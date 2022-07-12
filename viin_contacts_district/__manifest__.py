{
    'name': "Contact - District",
    'name_vi_VN': "Liên hệ - Quận/Huyện",

    'summary': """
Bridge module between contact and district
""",
    'summary_vi_VN': """
Mô đun cầu nối giữa Liên hệ và Quận/Huyện
""",

    'description': """
What it does
============
Show district management menu.

Key Features
============

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô đun này làm gì
=================
Hiện thị menu để quản lý danh sách quận/huyện.

Tính năng nổi bật
=================

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
    'category': 'Hidden',
    'version': '0.1.0',
    'depends': ['viin_base_district','contacts'],

    'data': [
        'views/contact_views.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
