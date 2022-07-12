# -*- coding: utf-8 -*-
{
    'name': "Repair Access",
    'name_vi_VN': "Quyền Sửa Chữa",
    'summary': """
Create new access group to grant access to Repair application
    """,
    'summary_vi_VN': """
Tạo nhóm truy cập mới để cấp quyền truy cập vào ứng dụng Sửa chữa
    """,
    'description': """
The Problem
===========
By default, only inventory users have access rights to Repair application. In many organization, a person in charge of repair may not have access right to inventory.

What it does
============
This module come to solve such issue by adding a new access group so that any one can be granted with access to Repair application when needed, without granted access to Inventory.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Đặt vấn đề
==========
Theo mặc định, chỉ người dùng kho mới có quyền truy cập vào ứng dụng Sửa chữa. Trong nhiều tổ chức, một người phụ trách sửa chữa có thể không có quyền truy cập vào kho.

Module này làm gì
=================
Mô-đun này giải quyết vấn đề như vậy bằng cách thêm một nhóm truy cập mới để bất kỳ ai cũng có thể được cấp quyền truy cập vào ứng dụng Sửa chữa khi cần, mà không được cấp quyền truy cập vào Kho.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['repair'],

    # always loaded
    'data': [
        'security/repair_security.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
