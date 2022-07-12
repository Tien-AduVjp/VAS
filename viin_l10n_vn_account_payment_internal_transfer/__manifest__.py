{
    'name' : 'Vietnam - Internal Transfer',
    'name_vi_VN' : 'Việt Nam - Chuyển tiền nội bộ',

    'summary': 'Allow users to use intermediary account or not when making Internal Transfer',
    'summary_vi_VN': 'Cho phép người dùng sử dụng tài khoản trung gian hoặc không khi thực hiện Chuyển tiền nội bộ',

    'description': """
Vietnam Internal Transfer Payment
=================================
* This module allow users to use intermediary account or not when making Internal Transfer

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Chuyển tiền nội bộ kế toán Việt Nam
===================================
* Module này cho phép người dùng sử dụng tài khoản trung gian hoặc không khi thực hiện Chuyển tiền nội bộ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author' : 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    'category' : 'Localization',
    'version' : '0.1.0',

    # any module necessary for this one to work correctly
    'depends' : ['l10n_vn_c133'],

    # always loaded
    'data' : [
        'views/res_config_settings_views.xml'
      ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False, # mark this as ['hr_timesheet'] after upgrade for Odoo 14
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
