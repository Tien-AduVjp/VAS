# -*- coding: utf-8 -*-
{
    'name': "PoS - c200 Fix",
    'name_vi_VN': "PoS - Sửa đổi tài khoản theo thông tư 200",

    'summary': """
Fix Wrong account in PoS Payment Methods for Vietnam based companies""",
    'summary_vi_VN': """
Sửa đổi tài khoản phải thu của khách hàng từ 132 thành 131 theo thông tư 200 cho các công ty Việt Nam""",

    'description': """
Key Features
============
* Fix Wrong account in PoS Payment Methods for Vietnam based companies

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Tính năng nổi bật
=================
* Cho phép sửa đổi tài khoản phải thu của khách hàng từ 132 thành 131 theo thông tư 200 cho các công ty Việt Nam

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version' : '0.9',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # any module necessary for this one to work correctly
    'depends': ['l10n_vn_c200', 'point_of_sale'],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
