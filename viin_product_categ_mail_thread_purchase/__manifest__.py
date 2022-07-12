{
    'name': "Product Category Chatter - Purchase",
    'name_vi_VN':"Theo dõi thay đổi Nhóm sản phẩm - Mua sắm",

    'summary': """
Integrate Product Category Chatter with Purchase
""",

    'summary_vi_VN': """
Tích hợp Product Category Chatter với Mua sắm
    	""",

    'description': """
This module track changes of the following field of the product category

- property_account_creditor_price_difference_categ

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Theo dõi sự thay đổi của trường Tài khoản chênh lệch giá của Nhóm sản phẩm

- property_account_creditor_price_difference_categ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Sales/Sales',
    'version': '0.1',
    'depends': ['viin_product_categ_mail_thread', 'purchase'],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
