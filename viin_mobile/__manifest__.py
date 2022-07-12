{
    'name': "Viindoo Mobile",
    'name_vi_VN': "Viindoo Mobile",
    'version': '0.1.0',
    'summary': """This module provides the core of the Viindoo Mobile App""",
    'summary_vi_VN': """Module này cung cấp tính năng cơ sở cho Ứng dụng Viindoo Mobile""",
    'description': """
What it does
============
This module provides the core of the Viindoo Mobile App


Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này cung cấp tính năng cơ sở cho Ứng dụng Viindoo Mobile

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'depends': ['mail', 'digest'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/assets.xml',
        'views/res_users_views.xml',
        'data/digest_data.xml',
    ],
    'qweb': [
        'static/src/xml/thread_window_mobile.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': ['mail'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
