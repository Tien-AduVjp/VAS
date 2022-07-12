# -*- coding: utf-8 -*-
{
    'name': "Partner Tracking Change",
    'name_vi_VN': "Theo dõi thay đổi thông tin đối tác",

    'summary': """
Tracking changes of partner information""",

    'summary_vi_VN': """
Theo dõi những sự thay đổi thông tin quan trọng của đối tác
    	""",

    'description': """
Key Features
============
* Allow to keep track on the changes of the Contact information with changing records attached to the Contact. 

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Cho phép theo dõi sự thay đổi của các trường thông tin ở phần Liên hệ bằng những ghi chú lịch sử thay đổi kèm theo Liên hệ đó.

Ấn bản được hỗ trợ
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
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
