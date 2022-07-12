# -*- coding: utf-8 -*-
{
    'name': "Employee Working Schedule",
    'name_vi_VN': "",

    'summary': """
Technical module to provide some utilities to work with employee working schedule""",

    'summary_vi_VN': """
Module kỹ thuật để cung cấp các tiện ích liên quan đến lịch làm việc của nhân viên
    	""",

    'description': """

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],

    # always loaded
    'data': [
        'views/resource_calendar_leaves_views.xml',
        'views/resource_calendar_views.xml',
    ],
    'images': [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 27.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
