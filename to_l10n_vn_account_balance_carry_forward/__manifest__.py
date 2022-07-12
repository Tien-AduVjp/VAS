{

    'name': 'Vietnam Account Balance Carry Forward',
    'nam__vi_VN': 'Kết chuyển số dư cuối kỳ - Kế toán Việt Nam',
    'version': '2.0.1',
    'category': 'Localization',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': 'Add forwarding rules in compliance with VAS',
    'summary_vi_VN': 'Thêm quy tắc kết chuyển số dư tài khoản theo Chuẩn mực kế toán Việt Nam',
    'description': """
Key Features
============
This application, upon installation, will create account balance carry forward rules according to the Vietnam Accounting Standards.

* 521 -> 511 (C200)
* 631 -> 632
* 511 -> 911
* 632 -> 911
* 711 -> 911
* etc
* 911 -> 4212 if closing fiscal year
* 33311 -> 1331

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",

    'description_vi_VN': """
Mô tả
=====
Khi được cài đặt, ứng dụng này sẽ tạo ra các quy tắc kết chuyển số dư tài khoản theo Chuẩn mực kế toán Việt Nam

* 521 -> 511 (C200)
* 631 -> 632
* 511 -> 911
* 632 -> 911
* 711 -> 911
* etc
* 911 -> 4212 nếu kết thúc năm tài chính
* 33311 -> 1331

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'depends': ['l10n_vn_c200', 'l10n_vn_c133', 'to_account_balance_carry_forward'],
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
