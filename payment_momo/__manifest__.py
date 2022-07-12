{
    'name': "MoMo Payment Acquirer",
    'name_vi_VN': "Thanh toán trực tuyến MoMo",

    'summary': """
Online payment integration with MoMo
        """,

    'summary_vi_VN': """
Tích hợp Thanh toán trực tuyến bằng MoMo
    	""",

    'description': """
Online payment integration with MoMo

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tích hợp Thanh toán trực tuyến bằng MoMo

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
        'views/payment_momo_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_views.xml',
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
