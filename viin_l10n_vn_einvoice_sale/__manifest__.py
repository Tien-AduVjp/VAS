{
    'name': 'E-invoice - Sale',
    'name_vi_VN': 'Hóa đơn điện tử - Bán hàng',

    'summary': """Integrate E-invoice with Sale""",
    'summary_vi_VN': """Tích hợp mô-đun Hóa đơn điện tử và Bán hàng""",

    'description': """
What it does
============
Integrate E-invoice module with Sale module

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Tích hợp mô-đun 'Hóa đơn điện tử ' và mô-đun 'Bán hàng'

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    'category': 'Localization',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['viin_l10n_vn_einvoice_common', 'sale'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False,  # set this as True after upgrading for Odoo 14
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
