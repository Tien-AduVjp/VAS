# -*- coding: utf-8 -*-
{
    'name': "Warehouse Improvement",
    'name_vi_VN': "Cải thiện kho hàng",

    'summary': """
Provide additional improvements to the default Odoo Warehouse/Inventory""",
    'summary_vi_VN': """
Cung cấp thêm các cải tiến bổ sung cho Kho hàng mặc định của Odoo """,

    'description': """
What it does
============
This module provides additional filters to help you find some criteria more easily besides the default filters of Odoo.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Module này cung cấp thêm các bộ lọc giúp bạn tìm kiếm một số tiêu chí dễ dàng hơn bên cạnh các bộ lọc mặc định của Odoo.

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_quant_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
