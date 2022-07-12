{
    'name': "Vietnam Driver License Classes",
    'name_vi_VN': "Giấy phép Lái Xe Việt Nam",
    'summary': """Vietnamese Localization for Fleet Driver""",
    'summary_vi_VN': """Giấy phép lái xe tại Việt Nam""",
    'description': """
What is does
============
This module adds Driver's License Classes Data for drivers in Vietnam

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Module này thêm dữ liệu giấy phép lái xe cho người lái xe ở Việt Nam.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_fleet_driver'],

    # always loaded
    'data': [
        'data/driver_license_class_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
