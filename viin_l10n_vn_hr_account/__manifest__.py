{
    'name': "Vietnam - HR Accounting",
    'name_vi_VN': "Kế toán Nhân sự - Việt Nam",

    'summary': """
Extending Human Resource Accounting module providing Vietnam Standards
    """,

    'summary_vi_VN': """
Mở rộng mô-đun cơ sở tích hợp kế toán và nhân sự theo Tiêu chuẩn Việt Nam
    """,

    'description': """
What it does
============
Extending Human Resource Accounting module providing Vietnam Standards

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mở rộng mô-đun cơ sở tích hợp kế toán và nhân sự theo Tiêu chuẩn Việt Nam

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Accounting/Human Resources',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_account', 'l10n_vn_common'],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
