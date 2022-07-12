{
    'name' : 'Vietnam - Account Detail Sheet (S38-DN)',
    'name_vi_VN': "Việt Nam - Sổ chi tiết tài khoản (S38-DN)",

    'summary': 'Vietnam Account Detail Sheet according to the template S38-DN',

    'summary_vi_VN': 'Sổ chi tiết tài khoản Việt Nam theo mẫu S38-DN',

    'description':"""
What it does
============
This application provides PDF and Excel version of the account detail sheet that is in compliance with the Circular No. 200/2014/TT-BTC dated 22 December 2014 of the Ministry of Finance of Vietnam.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cung cấp phiên bản PDF và Excel của sổ chi tiết tài khoản tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính Việt Nam.

Ấn bản được Hỗ trợ
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
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 24,
    'category': 'Accounting',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_l10n_vn_qweb_layout', 'to_account_counterpart'],

    # always loaded
    'data': [
        'data/data.xml',
        'wizard/l10n_vn_c200_s38dn_views.xml',
        'views/account_view.xml',
        'views/account_report_view.xml',
        'views/report_c200_s38dn.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
