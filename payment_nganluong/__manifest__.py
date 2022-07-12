{
    'name': "Ngan Luong Payment Acquirer",
    'name_vi_VN': "Thanh toán trực tuyến Ngân Lượng",

    'summary': """
Online payment integration with NganLuong
        """,

    'summary_vi_VN': """
Tích hợp Thanh toán trực tuyến bằng Ngân Lượng 
    	""",

    'description': """
Online payment integration with NganLuong

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tích hợp Thanh toán trực tuyến bằng Ngân Lượng 

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['payment', 'to_vietnam_bank_icons'],
    'data': [
        'data/scheduler_data.xml',
        'views/payment_nganluong_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_acquirer_views.xml',
        'views/payment_templates.xml',
        'views/assets.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 297.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
