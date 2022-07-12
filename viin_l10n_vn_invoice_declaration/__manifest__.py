{
    'name' : 'Vietnam - Invoicing/Bills Declaration',
    'name_vi_VN': 'Việt Nam - Bảng kê hóa đơn mua vào bán ra',

    'summary': 'Invoicing and Bills declaration for Vietnam based companies according to the templates 01-1/GTGT and 01-2/GTGT',

    'summary_vi_VN': 'Bảng kê hóa đơn, chứng từ hàng hóa, dịch vụ mua vào bán ra cho doanh nghiệp Việt theo mẫu 01-1/GTGT và 01-2/GTGT',

    'description':"""
What it does
============
This application provides Excel version of the Invoicing and Bills Declaration that is in compliance with the Circular No. 200/2014/TT-BTC dated 22 December 2014 of the Ministry of Finance of Vietnam.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cung cấp phiên bản Excel bảng sao kê hóa đơn, chứng từ hàng hóa, dịch vụ mua vào, bán ra theo mẫu ban hành kèm theo Thông tư số 119/2014/TT-BTC của Bộ Tài chính.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'Viindoo',
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 24,
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_tax_is_vat', 'to_legal_invoice_number'],

    # always loaded
    'data': [
        'data/account_tag.xml',
        'views/root_menu.xml',
        'wizards/l10n_vn_c119_01_gtgt_view.xml',
        'wizards/l10n_vn_c119_02_gtgt_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
