# -*- coding: utf-8 -*-
{
    'name': "Purchases Lines Numbering",
    'name_vi_VN': "Đánh số dòng đơn mua",   

    'summary': """
Enable Numbering on Purchases Lines""",
    'summary_vi_VN': """
Cho phép đánh số trên các dòng đơn mua""",
    'description': """

Key features
============
Show lines numbering on Purchases Order form and Purchases Request for Quotation PDF version

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Hiển thị số dòng trên form Đơn mua và Yêu cầu mua cho bản in PDF báo giá

Tính năng nổi bật
=================
Mô-đun này giúp hiển thị số thứ tự các dòng trong Đơn mua và Yêu cầu báo giá định dạng PDF

Ấn bản hỗ trợ
=============
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
    'category': 'Purchases',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/purchase_order_templates.xml',
        'views/purchase_quotation_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
