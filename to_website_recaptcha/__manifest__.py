{
    'name': "Website - ReCaptcha",
    'name_vi_VN': "Website - ReCaptcha",
    'summary': """
Base module for recaptcha implement in website forms.
        """,
    'summary_vi_VN': """
Module cơ sở cho việc tích hợp recaptcha vào form trên website.
        """,
    'description': """
What it does
============
Add ReCaptcha validation into website,protects your websites from spam and abuse.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Thêm Google Recaptcha vào website, để tránh spam bằng các robot tự động.

Ấn bản được Hỗ trợ
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
    'depends': ['website', 'google_recaptcha'],

    # always loaded
    'data': [
        'views/assets.xml',

    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
