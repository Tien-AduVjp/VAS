# -*- coding: utf-8 -*-
{
    'name': "Sales with Affiliates",
    'name_vi_VN': "Bán Hàng Với chương trình cộng Tác",

    'summary': """
Affiliate Management with Sales Management integration""",
    'summary_vi_VN': """
Tích hợp ứng dụng Cộng tác viên với Quản lý Bán hàng
    	""",

    'description': """
Key Features
============
* Sales Management Integration: Each quotation/sales order form is added with the AffCode field to refer that the order was placed with help of an affiliate
* With this module installed, you can filter the affiliate order by AffCode field added in each quotation. It is also used to calculate the affiliate commission based on the commission rule and the sales order value. 

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
===================
* Tích hợp quản lý bán hàng: Mỗi báo giá và đơn hàng đều được thêm trường Mã cộng tác viên để phân biệt các đơn bán cộng tác viên và đơn bán thông thường
* Có thể lọc các đơn bán công tác viên bằng trường Mã cộng tác trên báo giá. Nó cũng được sử dụng để tính toán hoa hồng cộng tác viên dựa trên quy tắc tính hoa hồng và giá trị của đơn hàng

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_affiliate', 'sale'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/affiliate_code_views.xml',
        'views/sale_order_views.xml',
        'report/affiliate_report.xml',
        'report/sale_report.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
