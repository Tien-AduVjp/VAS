# -*- coding: utf-8 -*-
{
    'name': "Lines Count on Journal Entries",
    'name_vi_VN': "Đếm dòng trên Bút toán sổ nhật ký",
    
    'summary': """
Count lines on Journal Entries""",
    'summary_vi_VN': """
Đếm dòng trên Bút toán sổ nhật ký""",

    'description': """
Key Features
============
* This module adds a new field to count number of lines (aka Journal Items) of a Journal Entry to allow you filter for journal entries with lines count criteria.
* This also adds a new filter named "Large Entries" on the Journal Entry list view so that you can quickly find entries having more than 100 lines

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Module này thêm một trường mới để đếm số lượng dòng (Phát sinh kế toán) của Bút toán sổ nhật ký để cho phép bạn lọc các Bút toán sổ nhật ký với tiêu chí đếm dòng.
* Điều này cũng thêm một  bộ lọc mới có tên "Bút toán lớn" trên chế độ xem danh sách Bút toán sổ nhật ký  để bạn có thể nhanh chóng tìm thấy các bút toán có hơn 100 dòng.

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
    'category': 'Hidden',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
