{
    'name': "Enterprise Marks - Website",
    'name_vi_VN': "Ẩn tính năng Enterprise - Website",

    'summary': """
Hide Enterprise features in Website Settings""",

    'summary_vi_VN': """
Ẩn các tính năng Enterprise trong Thiết lập Website""",

    'description': """
What it does
============
* This module helps to hide Enterprise features in Website Settings.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
* Module này giúp ẩn các tính năng Enterprise trong Thiết lập Website.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    # 'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
