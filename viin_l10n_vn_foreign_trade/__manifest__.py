# -*- coding: utf-8 -*-
{
    'name': "Vietnam - Foreign Trade",
    'old_technical_name': 'to_l10n_vn_foreign_trade',
    'name_vi_VN': "Ngoại thương - Việt Nam",
    'summary': """Extending Foreign Trade & Logistics module providing Vietnam Standards""",
    'summary_vi_VN': """Mở rộng mô-đun Ngoại Thương & Logistics theo Tiêu chuẩn Việt Nam""",
    'description': """
What it does
============
Extending Foreign Trade & Logistics module providing Vietnam Standards

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Mở rộng mô-đun Ngoại Thương & Logistics theo Tiêu chuẩn Việt Nam

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_foreign_trade', 'viin_l10n_vn_vat_counterpart', 'viin_account'],

    # always loaded
    'data': [
        'data/account_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
