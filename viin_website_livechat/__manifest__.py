# -*- coding: utf-8 -*-
{
    'name': "Viin - Website Live Chat",
    'name_vi_VN': "Viin - Chat trực tuyến trên website",

    'summary': """
Advanced Livechat features additional to the Odoo core's
""",

    'summary_vi_VN': """
Thêm các tính năng livechat bổ sung cho tính năng mặc định của Odoo
""",

    'description': """
What it does
============

1. Internal Operators can now trigger chat window open with visitors.
2. Multilingual Livechat supports

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

1. Cho phép người dùng nội bộ khởi chạy cửa sổ chat với khách ghé thăm website
2. Hỗ trợ đa ngôn ngữ cho cửa sổ chat

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
    'version': '0.1',
    'depends': ['website_livechat'],
    'data': [
        'views/website_livechat.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': ['website_livechat'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
