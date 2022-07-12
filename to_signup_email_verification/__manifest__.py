{
    'name': "Signup Email Verification",
    'name_vi_VN': 'Thẩm định Email khi Đăng ký',
    'summary': """
Add an email verification step for account registration activation
""",
    'summary_vi_VN': """
Thêm bước xác nhận email để kích hoạt tài khoản đăng ký
    	""",

    'description': """
What it does
============
This module adds a step to require newly registered users to activate their account via email after signup

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Chức năng
=========
Module này sẽ thêm 1 bước xác nhận để kích hoạt tài khoản qua email sau khi người dùng đăng ký tài khoản.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
""",

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['auth_signup', 'to_token_expiration'],

    # always loaded
    'data': [
        'views/signup_template.xml',
    ],

    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
