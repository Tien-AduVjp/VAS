# -*- coding: utf-8 -*-
{
    'name': "Website Odoo Versioning Documentation",
    'name_vi_VN': "Quản Lý tài liệu Website theo phiên bản Odoo",

    'summary': """
Manage and Publish Odoo documents on your websites""",
    'summary_vi_VN': 'Quản lý và xuất bản tài liệu trên Website theo phiên bản Odoo',

    'description': """
What it does
============
If you need to manage multiple versions of the same document that correspond to the versions of Odoo (eg. : user manual for Accounting module Odoo versions 12.0, 13.0, 14.0), 
this module integrates Odoo version management with documentation on Website, that allows publishing documents according to each Odoo version in the Documents section, Website module.

Key Features
============
- Integrate Odoo Version Management with Website Documentation
- Manage and publish your documents with Odoo versioning
- When a website viewer selects an Odoo version, the website will display the document corresponding to that Odoo version.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Mô tả
=====
Để quản lý nhiều phiên bản của cùng một tài liệu tương ứng với các phiên bản của Odoo (VD: tài liệu hướng dẫn sử dụng cho phân hệ Kế toán phiên bản Odoo 12.0, 13.0, 14.0),
module này tích hợp quản lý phiên bản Odoo với tài liệu trên Website, cho phép xuất bản tài liệu theo từng phiên bản Odoo trong mục Tài liệu, phân hệ Website.

Tính năng nổi bật
=================
- Tích hợp Quản Lý Phiên Bản Odoo với Tài liệu Website
- Quản lý và xuất bản tài liệu theo từng phiên bản Odoo
- Khi người xem lựa chọn phiên bản Odoo trên website, website sẽ hiển thị tài liệu tương ứng với phiên bản Odoo đó

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
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_website_docs', 'to_website_odoo_version'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/website_doc_category_views.xml',
        'views/website_document_content_views.xml',
        'views/website_document_views.xml',
        'views/assets.xml',
        'views/templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': ['static/src/xml/doc.xml'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
