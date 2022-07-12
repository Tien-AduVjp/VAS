{
    'name': "Accounting Customization",
    'name_vi_VN': "Tùy biến Kế toán",

    'summary': """
Base module for Accounting customization""",

    'summary_vi_VN': """
Module cơ sở cho việc tùy biến Kế toán
    	""",

    'description': """
What it does
============
This module provides a few customizations for accounting and serves as the basis for further modules to expand on

Key Features
============
1. Add VAT Counterpart Account into Company

   * This field will be filled automatically by l10n modules

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô đun này cung cấp một vài tùy biến cho phần kế toán và làm cơ sở để các mô đun khác tiếp tục mở rộng

Tính năng nổi bật
=================
1. Thêm trường Tài khoản đối ứng Thuế GTGT vào Công ty

   * Trường này sẽ được điền tự động bỏi các mô đun bản địa hóa

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
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
    ],
    'images': [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
