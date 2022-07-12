# -*- coding: utf-8 -*-
{
    'name': "Document Templates Management",
    'name_vi_VN': "Quản lý các mẫu tài liệu",

    'summary': """Manage document templates, allow users to create document templates and preview them before printing.
        """,

    'summary_vi_VN': """Quản lý các mẫu tài liệu, cho phép tạo và xem trước các mẫu tài liệu trước khi in.
        """,

    'description': """
What it does
============
This module is to manage document templates, create new ones and preview them before exporting to pdf file.

Key Features
============
* Manage all the document templates in a place
* Create document templates applied for different objects, like: sales of order, purchase of order, invoice, etc
* Preview the created document before exporting to pdf file
* This is a base module. Applying templates for objects depends on the intergration of relavtive modules

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Quản lý các mẫu tài liệu, tạo mới và xem trước khi xuất thành bản pdf.

Tính năng nổi bật
=================
* Quản lý tất cả các mẫu tài liệu tại một nơi
* Tạo mới một mẫu tài liệu gắn với một đối tượng trong phần mềm như đơn hàng bán, đơn hàng mua, hóa đơn, ...
* Xem trước các mẫu tài liệu này trước khi xuất thành bản PDF
* Đây là mô-đun cơ sở, việc có thể áp dụng mẫu tài liệu vào đối tượng nào phụ thuộc vào việc thích hợp với các mô-đun liên quan

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/document_template_preview_view.xml',
        'views/document_template_views.xml',

    ],
    'images' : ['static/description/main_screenshot.png'],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
