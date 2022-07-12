{
    'name': "Documents - Purchase",
    'name_vi_VN': "Quản lý Tài liệu Mua",

    'summary': """
Purchase Documents""",

    'summary_vi_VN': """
Quản lý Tài liệu Mua""",

    'description': """

What it does
============
This bridge module between Document Management System and Purchase.

Key Features
============
* Create data and demo data for workspace, team, tag, action, auto generate rule.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Mô tả
=====
Mô đun cầu nối giữa Quản lý tài liệu và Mua.

Tính năng nổi bật
=================
* Tạo sẵn dữ liệu cho Thư mục, đội nhóm, tag, hành động, quy tắc tạo tài liệu tự động.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Productivity/Documents',
    'version': '0.1.0',
    'depends': ['viin_document','purchase'],
    'data': [
        'data/document_tag_category_data.xml',
        'data/document_tag_data.xml',
        'data/document_team_data.xml',
        'data/document_workspace_data.xml',
        'data/document_auto_generate_rule_data.xml',
    ],
    'demo': [
        'demo/document_document_demo.xml',
    ],
    'images' : [

    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'subscription_price': 0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
