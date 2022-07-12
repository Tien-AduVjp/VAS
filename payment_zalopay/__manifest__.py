{
    'name': "ZaloPay Payment Acquirer",
    'name_vi_VN': "Thanh toán trực tuyến ZaloPay",

    'summary': """
Online payment integration with ZaloPay
        """,

    'summary_vi_VN': """
Tích hợp Thanh toán trực tuyến bằng ZaloPay
    	""",

    'description': """
Online payment integration with ZaloPay

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tích hợp Thanh toán trực tuyến bằng ZaloPay

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
    'version': '0.1.0',
    'depends': ['payment', 'to_vietnam_bank_icons', 'to_currency_conversion_diff'],
    'data': [
        'data/payment_cron.xml',
        'views/payment_zalopay_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_views.xml',
        #'views/assets.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'application': False,
    'auto_install': False,
    'price': 297.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
