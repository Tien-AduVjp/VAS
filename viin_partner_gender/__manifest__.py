{
    'name': "Partner Gender",
    'name_vi_VN': "Giới tính đối tác",

    'summary': """
        Manage partner gender
    """,

    'summary_vi_VN': """
        Quản lý giới tính đối tác
    """,

    'description': """

What it does
============
- Manage partner gender

Key Features
============
- Add gender field to partner
- Add gender search filter for partner
- Add gender search group for partner

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Ứng dụng này làm gì
===================
- Quản lý giới tính đối tác

Tính năng chính
===============
- Bổ sung thêm trường giới tính cho đối tác
- Bổ sung bộ lọc tìm kiếm theo giới tính của đối tác
- Bổ sung nhóm đối tác theo giới tính


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/res_partner_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 4.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
