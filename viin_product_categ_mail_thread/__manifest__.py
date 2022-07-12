{
    'name': "Product Category Chatter",
    'name_vi_VN':"Theo dõi thay đổi Nhóm sản phẩm",

    'summary': """
Product Category OpenChatter (aka Mail Thread) support and fields change tracking.
""",

    'summary_vi_VN': """
OpenChatter cho Nhóm sản phẩm và theo dõi thay đổi các trường quan trọng của nó.
""",

    'description': """
Key Features
============

This module adds OpenChatter (aka Mail Thread) support for Product Category and track changes of the following fields of its:

    * name
    * parent_id
    * property_account_income_categ_id
    * property_account_expense_categ_id

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================

Module này bổ sung phần trao đổi thông tin (Chatter) cho Nhóm sản phẩm và lưu lại lịch sử khi thay đổi thông tin của các trường sau đây:

    * name
    * parent_id
    * property_account_income_categ_id
    * property_account_expense_categ_id

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
    'category': 'Productivity',
    'version': '0.1',
    'depends': ['account'],
    'data': [
        'views/product_category_views.xml',
    ],
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
