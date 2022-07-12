{
    'name': "Backdate Operations Access Rights",
    'name_vi_VN': "Quyền nhập Ngày trong Quá khứ",

    'summary': """
Access group for backdate operations""",

    'summary_vi_VN': """
Nhóm quyền cho các hoạt động với ngày thực hiện trong quá khứ
        """,

    'description': """
What is does
============
This module is intended for other backdate-related modules to extend such as Stock Transfers Backdate, Inventory Backdate, Sales Confirmation Backdate, etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Module này làm gì
=================
Module này là module cơ sở để các module liên quan đến backdate có thể kế thừa.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': 'https://v14demo-vn.viindoo.com',
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'wizard/abstract_backdate_wizard_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
