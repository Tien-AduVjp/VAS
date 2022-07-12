# -*- coding: utf-8 -*-
{
    'name': "Legal Invoice Number",
    'name_vi_VN': "Số hóa đơn giá trị gia tăng",

    'summary': """
An additional number for invoice""",

    'summary_vi_VN': """
Một số bổ sung cho hóa đơn
        """,

    'description': """
Key Features
============
A new field 'Legal Number' has been added to the invoice model to allow users to:

* Input an additional invoice number for legal purpose
* Search invoice by legal number

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
Một trường mới 'Số Hoá đơn GTGT' đã được thêm vào hóa đơn để cho phép người dùng:

* Nhập bổ sung một mã số hoá đơn giá trị gia tăng theo luật định
* Tìm kiếm hóa đơn theo số hóa đơn giá trị gia tăng

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'data/ir_action_server_data.xml',
        'views/account_move_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
