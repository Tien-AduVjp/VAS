# -*- coding: utf-8 -*-
{
    'name': "Accounting Report Flag",
    'name_vi_VN': "Đánh dấu Loại khỏi Báo cáo Kế toán",

    'summary': """
Excluded in Legal Reports filtering for accounting journal entries and journal items""",
    'summary_vi_VN': """
Đánh dấu bút toán và phát sinh kế toán để loại ra khỏi các báo cáo kế toán""",
    'description': """
This module adds a boolean field of Excluded in Legal Reports in accounting journal entries and journal items.
This may be useful for other reporting modules to manipulate report contents.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này thêm trường đánh dấu Loại khỏi Báo cáo trên các phát sinh kế toán và bút toán sổ nhật ký.
Điều này giúp cho các module liên quan đến báo cáo kế toán có thể thay đổi nội dung báo cáo bằng cách loại trừ số liệu được đánh dấu Loại khỏi Báo cáo.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/module_security.xml',
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/account_move_line_views.xml',
        'views/account_move_line_server_actions.xml',
        'views/account_move_server_actions.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
