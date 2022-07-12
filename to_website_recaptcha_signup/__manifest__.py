{
    'name': "Website ReCaptcha -Signup",
    'name_vi_Vn': "Website ReCaptcha - Đăng ký",
    'summary': """
ReCaptcha validation in Signup Form.
        """,
    'summary_vi_VN': """
Tích hợp ReCaptcha trong Form Đăng kí.
        """,
    'description': """
What it does
============
Add ReCaptcha validation in Signup Form,protects your websites from spam and abuse.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Thêm Google Recaptcha vào form đăng kí, để tránh spam bằng các robot tự động.
Ấn bản bản hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_website_recaptcha', 'auth_signup'],

    # always loaded
    'data': [
        'views/website_signup_template.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
