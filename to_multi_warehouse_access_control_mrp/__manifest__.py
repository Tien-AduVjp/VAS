# -*- coding: utf-8 -*-
{
    'name': "Multi-Warehouse Access Control - Manufacturing",
    'name_vi_VN': "Kiểm Soát Truy Cập Đa Kho - Sản Xuất",

    'summary': """
Integrate Multi-Warehouse Access Control with Manufacturing""",
    'summary_vi_VN': """
Tích hợp Kiểm soát truy cập Đa Kho với Sản xuất
        """,

    'description': """
What it does
============
Grant 'Inventory / Users: Own Documents' read access to manufactoring orders

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Phân quyền bổ sung cho nhóm người dùng 'Kho / Chỉ tài liệu của mình' để có thể đọc lệnh sản xuất

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_multi_warehouse_access_control', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
