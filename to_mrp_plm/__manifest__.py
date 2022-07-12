{
    'name': 'Product Lifecycle',
    'name_vi_VN': 'Vòng đời Sản phẩm',
    'summary': """Bill of Materials, Routings, Versions, Engineering Change Orders""",
    'summary_vi_VN': 'Định mức nguyên liệu, quy trình, phiên bản, lệnh thay đổi kỹ thuật',
    'description': """
What it does
============
This module provides product life cycle management feature in the Manufacturing module

Key Features
============
* Versioning of Bill of Materials and Routings
* Different approval processes depending on the type of change order

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Mô tả
=====
Quản lý vòng đời của sản phẩm trong phân hệ Sản xuất

Tính năng nổi bật
=================
* Đánh số phiên bản định mức nguyên liệu và quy trình
* Cho phép quy trình phê duyệt khác nhau tùy thuộc vào loại thay đổi

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'sequence': 50,
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'data/mrp_data.xml',
        'views/assets.xml',
        'views/root_menu.xml',
        'views/mrp_bom_views.xml',
        'views/mrp_eco_bom_change_views.xml',
        'views/mrp_eco_routing_change_views.xml',
        'views/mrp_eco_stage_views.xml',
        'views/mrp_eco_tag_views.xml',
        'views/mrp_eco_views.xml',
        'views/mrp_eco_type_views.xml',
        'views/product_views.xml',
    ],
    'qweb': [
        'static/src/xml/mrp_plm_templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': ['data/mrp_data.xml'],
    'images': [
        'static/description/main_screenshot.png'
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 252.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
