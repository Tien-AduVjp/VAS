{
    'name': "VNPay Payment Acquirer",
    'name_vi_VN': "Thanh toán trực tuyến VNPay",

    'summary': """
Online payment integration with VNPay
""",

    'summary_vi_VN': """
Tích hợp thanh toán trực tuyến với VNPay
    	""",

    'description': """
Key Features
============
Online payment intergration with VNPay

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Tích hợp thanh toán trực tuyến với VNPay

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Accounting',
    'version': '0.2',
    'depends': ['payment', 'to_vietnam_bank_icons', 'to_currency_conversion_diff'],
    'data': [
        'views/payment_vnpay_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_acquirer_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'application': False,
    'auto_install': False,
    'price': 549.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
