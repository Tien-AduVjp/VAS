{
    'name': "Automatic Currency Rates Update by ACB bank",
    'name_vi_VN': 'Tự Động Cập Nhật Tỷ Giá Tiền Tệ Theo Ngân Hàng ACB',
    'summary': """
Automatic currency rates update by ACB bank""",
    'summary_vi_VN': """
Tự động cập nhật tỷ giá ngoại tệ theo ngân hàng ACB""",
    'description': """
What it does
============
This is the legacy module of '''viin_auto_currency_rate''', it enables automatic updates exchange rates from ACB (Asia Commercial Bank) in the Accounting module.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Là module kế thừa của module '''viin_auto_currency_rate''', cho phép tự động cập nhật định kỳ tỷ giá hối đoái từ ngân hàng ACB trong phân hệ Kế toán.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Accounting',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['viin_auto_currency_rate'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
