{
    'name': "Subscription - Accounting",
    'name_vi_VN': '',
    'summary': "Base module for integrate subscription with accounting",
    'summary_vi_VN': "Module cơ sở để tích hợp kế toán với thuê bao",
    'description': """
What it does
============
Base module for integrate subscription with accounting

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Module cơ sở để tích hợp kế toán với thuê bao

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'category': 'Hidden',
    'version': '0.1',
    'author': 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
