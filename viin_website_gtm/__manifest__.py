{
    'name': "Google Tag Manager",
    'name_vi_VN': "Google Tag Manager",

    'summary': """
Integrate Google Tag Manager with websites
    """,

    'summary_vi_VN': """
Tích hợp Google Tag Manager cho các website
    	""",

    'description': """
What it does
============
1. Add settings to install Google Tag Manager to a website. Support multi websites.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

Tính năng chính
===============
1. Thêm cài đặt để tích hợp Google Tag Manager cho riêng từng website một.

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
    'category': 'Website',
    'version': '0.1',
    'depends': ['website'],
    'data': [
        'views/website_templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
