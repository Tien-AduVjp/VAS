# -*- coding: utf-8 -*-
{
    'name': "Multi-Warehouse Access Control - Vietnam Legal Stock Reports",
    'name_vi_VN': "Kiểm Soát Truy Cập Đa Kho - Báo cáo Kho luật định Việt Nam",

    'summary': """
Grant 'Inventory / Warehouse Manager' access to Vietnam Legal Stock Reports""",
    'summary_vi_VN': """
Phân quyền bổ sung cho nhóm người dùng 'Kho / Quản lý kho' để truy cập báo báo Kho luật định Việt Nam
        """,

    'description': """
What it does
============
Grant 'Inventory / Warehouse Manager' access to Vietnam Legal Stock Reports

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Phân quyền bổ sung cho nhóm người dùng 'Kho / Quản lý kho' để truy cập báo báo Kho luật định Việt Nam

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['to_multi_warehouse_access_control', 'to_l10n_vn_stock_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_report_menu_view.xml',
    ],
    'images' : [],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
