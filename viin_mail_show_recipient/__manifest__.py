{
    'name': "Mail Show Recipients",
    'name_vi_VN': "Hiển thị danh sách người nhận trong email",

    'summary': """
        Allows displaying email recipients in the email body
    """,

    'summary_vi_VN': """
        Cho phép hiển thị những người nhận được email trong nội dung của email
    """,

    'description': """
Problem
-------
By default, when sending a message, it will also send an email to all followers, but the followers don't know who the email was sent to.

Solution
--------
This module allows followers to know to whom this email was sent

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Vấn đề
------
Mặc định, khi gửi tin hệ thống sẽ gửi một email thông báo cho tất cả những người theo dõi nhưng họ sẽ không biết email này được gửi cho những người nào khác.

Giải pháp
---------
Module này cho phép những người theo dõi nhận được email sẽ biết được email được gửi cho những ai.

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

    'category': 'Discuss',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded;,;
    'data': [
        'data/mail_data.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    # only loaded in demonstration mode
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
