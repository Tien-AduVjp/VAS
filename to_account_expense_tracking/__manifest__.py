# -*- coding: utf-8 -*-

{
    'name': 'Accounting - HR Expense Tracking',
    'name_vi_VN': 'Kế toán - Theo vết Chi tiêu',
    
    'summary': 'Find and Track HR Expense related journal items and journal entries',
    'summary_vi_VN': 'Tìm và truy vết các bút toán và phát sinh kế toán có nguồn gốc từ chi tiêu (HR)',
    
    'version': '1.0.1',
    'category': 'Accounting/Expenses',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'description': """
What it does
============
This module create link between account entries and hr expenses to easy trace expense account entry.
  
* Allow group by expense on journal entries/items list view
* Allow filter journal entries/items which are expense entries/items
* Link journal entry to hr expense

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
""",

   'description_vi_VN': """
Module này làm gì
=================
Module này cho phép liên kết các bút toán với chi tiêu để dễ dàng truy xuất nguồn gốc các bút toán chi tiêu

* Cho phép nhóm theo chi tiêu trên danh sách bút toán và phát sinh bút toán
* Cho phép lọc ra các bút toán/phát sinh liên quan đến chi tiêu
* Liên kết bút toán với chi tiêu

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition
    """,

    'depends': ['hr_expense'],
    'data': [
        'views/account_move_line.xml',
        'views/account_move.xml'
        ],
    
    'demo': [],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': [],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
