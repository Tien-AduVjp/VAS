{

    'name': 'Vietnam Account Balance Carry Forward',
    'nam__vi_VN': 'Kết chuyển số dư cuối kỳ - Kế toán Việt Nam',
    'version': '2.0.0',
    'category': 'Localization',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Add forwarding rules in compliance with VAS',
    'summary_vi_VN': 'Thêm quy tắc kết chuyển số dư tài khoản theo Chuẩn mực kế toán Việt Nam',
    'description': """
Key Features
============
This application, upon installation, will create account balance carry forward rules according to the Vietnam Accounting Standards.

* 521 -> 511
* 511 -> 911
* 711 -> 911 
* 61x -> 911
* 62x -> 911
* etc
* 911 -> 4212 if closing fiscal year

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    
    'description_vi_VN': """
Mô tả
=====
Khi được cài đặt, ứng dụng này sẽ tạo ra các quy tắc kết chuyển số dư tài khoản theo Chuẩn mực kế toán Việt Nam

* 521 -> 511
* 511 -> 911
* 711 -> 911 
* 61x -> 911
* 62x -> 911
* etc
* 911 -> 4212 nếu kết thúc năm tài chính

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    
    'depends': ['l10n_vn_c200', 'to_account_balance_carry_forward'],
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
