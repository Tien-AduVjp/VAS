# -*- coding: utf-8 -*-
{
    'name': "Leaves Limit per Period",
    'name_vi_VN': "Giới Hạn Nghỉ Phép",
    'summary': """Add leave limit per period for Leave Types""",
    'summary_vi_VN': """
Thêm giới hạn nghỉ phép cho mỗi loại nghỉ phép""",
    'description': """
The Problem
===========
By default, Odoo allow leaves allocation with a total number of leaves allowed. However, it does not control if the allocation for a period of time. 

*For example: You can allocate 12 days of Legal Leave but you cannot limit how many leave days for a period of month or year.*
 
What it does
============

This module improves leave controlability by allowing leave managers to set number of allowed leaves per period for each and every leave type.

*For example, they can allocate 12 leave days for an employee but he can limit him to not leave more than 2 days per month.*
        
The following periods are supported:
------------------------------------
* Leaves Limit per Month
* Leaves Limit per Quarter
* Leaves Limit per Year

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Đặt vấn đề
==========
Theo mặc định, Odoo cho phép phân bổ nghỉ phép với tổng số ngày nghỉ được phép. Tuy nhiên, nó không thể kiểm soát nếu phân bổ trong một khoảng thời gian. 

*Ví dụ: Bạn có thể phân bổ 12 ngày nghỉ phép hợp pháp nhưng bạn không thể giới hạn số ngày nghỉ trong một tháng hoặc năm.*
 
Module này làm gì
=================
Mô-đun này cải thiện khả năng kiểm soát nghỉ phép bằng cách cho phép người quản lý nghỉ phép đặt số lượng ngày nghỉ được phép trong mỗi khoảng thời gian cho mỗi loại nghỉ phép.

*Ví dụ: Họ có thể phân bổ 12 ngày nghỉ cho một nhân viên nhưng họ có thể giới hạn anh ta không được nghỉ quá 2 ngày mỗi tháng.*
        
Các khoảng thời gian sau được hỗ trợ:
-------------------------------------
* Giới hạn ngày nghỉ mỗi tháng
* Giới hạn ngày nghỉ mỗi quý
* Giới hạn ngày nghỉ mỗi năm

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_leave_type_views.xml',
        'views/hr_leave_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
