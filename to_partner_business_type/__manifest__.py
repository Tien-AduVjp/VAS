{
    'name': "Partner Business Type Management",
    'name_vi_VN': 'Quản Lý Loại Hình Doanh Nghiệp',
    'summary': """
Manage business type""",
    'summary_vi_VN': """
Quản lý các loại hình doanh nghiệp""",
    'description': """
Key Features
============
* Add Business Type field on the Contact form.
* Search Contacts by Business type.
* Manage Business types.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
* Thêm trường Loại hình doanh nghiệp trên hồ sơ Liên hệ.
* Tìm kiếm Liên hệ theo Loại hình doanh nghiệp.
* Quản lý các loại hình doanh nghiệp.

Ấn bản được hỗ trợ
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
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/business_type_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
