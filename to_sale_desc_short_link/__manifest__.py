{
    'name': "Shorten URLs in Sales Order Line Description",
    'name_vi_VN': "Rút gọn URLs trong Mô Tả dòng Đơn Bán",

    'summary': """
Replace long URLs in sale order line description with short URLs""",

    'summary_vi_VN': """
Thay thế URL dài ở mô tả dòng đơn bán thành URL ngắn""",

    'description': """
What it does
============
This module replaces long URLs in sale order line description with short URLs using Odoo's native link tracker

Key Features
============
* Simplify and shorten the URLs in the Sales Orders or Quotaions description in Sales app 
* Apply to the "add a note" section in Order Lines in the same app as well

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này sử dụng tính năng Theo vết link trong Odoo để thay thế URLs dài thành URLs ngắn ở mô tả dòng đơn bán

Tính năng nổi bật
=================
* Đơn giản hóa và rút gọn URLs ở trong phần mô tả đơn bán hoặc báo giá của ứng dụng Bán Hàng. 
* Hỗ trợ áp dụng với cả phần ghi chú trong thanh Chi tiết đơn bán.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'to_shorten_url'],

    # always loaded
    'data': [
        'data/utm_source_data.xml',
        'data/ir_action_server.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 81.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
