{
    'name': "Inter Company Base",
    'name_vi_VN': 'Mô-đun liên công ty cơ sở',
    'summary': """
Base module for inter-company flows
        """,

    'summary_vi_VN': """
Module Cơ sở cho các quy trình liên công ty
    	""",

    'description': """
What it does
============
* This module allows users to enabling inter-company features for each module: Sale/Purchase, Invoice, Stock

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Đây là module cơ sở cho phép kích hoạt tính năng giao dịch liên công ty cho từng phân hệ: Mua/Bán, Hóa đơn, Kho 

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odooo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_enterprice_marks_inter_company'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    # only loaded in demonstration mode
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
