# -*- coding: utf-8 -*-
{
    'name': "Website Document Odoo Category Data",
    'name_vi_VN': "Quản Lý Danh mục tài liệu Website theo phiên bản Odoo",

    'summary': """
Default category data for Odoo documentation""",
    'summary_vi_VN': 'Quản lý Danh mục tài liệu trên Website theo phiên bản Odoo',

    'description': """
Key Features
============
* This module will automatically pre-install for you nearly 40 document categories to start using right away on the Website module.
* These categories are divided into two main sections:

    * Odoo User Documentation/Practical Information: includes general categories such as Getting Started, Process Management, Legal, Contributing, etc.
    * Odoo User Documentation/Applications: includes categories containing system modules such as Purchase, Inventory, Accounting, etc.

* You can delete/edit/create/import/export these categories as you wish.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
* Mô-đun này sẽ tự động cài đặt sẵn cho bạn gần 40 danh mục tài liệu để bắt đầu sử dụng ngay trên phân hệ Website.
* Các danh mục được chia làm 2 phân khúc chính:

    * Hướng dẫn Người dùng Odoo/Thông tin thực nghiệm: gồm có những danh mục chung như Những bước đầu tiên, Quản lý quy trình, Luật định, Đóng góp,...
    * Hướng dẫn Người dùng Odoo/Các ứng dụng: gồm có những danh mục chứa các phân hệ của hệ thống như Mua, Kho vận, Kế toán,...

* Bạn có thể xóa/sửa/thêm/nhập/trích xuất các danh mục theo ý muốn.

Ấn bản được hỗ trợ
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
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_website_docs_odoo', 'to_git'],

    # always loaded
    'data': [
        'data/category_data.xml',
        'views/git_branch_views.xml',
        'views/website_doc_category_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
