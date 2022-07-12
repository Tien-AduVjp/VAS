{
    'name' : 'Foreign Trade & Logistics Currency Rate',
    'old_technical_name': 'to_foreign_trade_currency_rate',
    'name_vi_VN': 'Tỷ Giá Tiền Tệ Ngoại Thương & Logistics',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': 'Foreign Trade & Logistics Support Bank Currency Rate',
    'summary_vi_VN': 'Hỗ trợ Tỷ giá Tiền tệ Ngoại Thương & Logistics',
    'category': 'Foreign Trade',
    'sequence': 24,
    'description': """
What it does
============
Apply transfer rate in custom declaration

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Module này làm gì
=================
Áp dụng tỷ giá giao dịch trong tờ khai hải quan

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'depends': ['viin_foreign_trade', 'to_bank_currency_rate'],
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
