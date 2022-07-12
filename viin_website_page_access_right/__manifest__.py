{
    'name' : "Website Page Access Rights",
    'name_vi_VN': "Quyền truy cập trang Web",

    'summary': "Allow group Restricted Editor to create, write, delete Website page",

    'summary_vi_VN': "Cho phép nhóm quyền 'Điều chỉnh giới hạn' có thể thêm, sửa, xóa bài viết của chính họ trên trang Web",

    'description':"""
What it does
============
This module provides the Create, Write, Delete Website page and can not publish or unpublish documents with group
"Website page / User: Restricted Editor".

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô đun cung cấp quyền Thêm, sửa , xóa, không được xuất bản tài liệu với nhóm
"Website page / Người dùng: Điều chỉnh giới hạn".

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'Viindoo',
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 24,
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/website_nabar_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
