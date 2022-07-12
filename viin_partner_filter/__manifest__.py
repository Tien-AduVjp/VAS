{
    'name': "Partner Filtering",
    'name_vi_VN': "Lọc đối tác",
    'summary': """
Support filtering partner by phone or mobile criteria
        """,
    'summary_vi_VN': """
Hỗ trợ lọc đối tác theo tiêu chí số điện thoại hoặc di động
         """,
    'description': """
What it does
============
* Support filtering partner by phone or mobile criteria when it contains especial characters as: -, \*, :, ., (,)........

Key Features
============
* Filtering partner by phone criteria
* Filtering partner by mobile criteria
* Filtering partner by phone or mobile criteria

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Hỗ trợ lọc đối tác theo tiêu chí số điện thoại hoặc di động khi số điện thoại hoặc di động chứa các kí tự đặc biệt như: -, \*, :, ., (,)........

Tính năng nổi bật
=================
* Hỗ trợ lọc đối tác theo tiêu chí số điện thoại
* Hỗ trợ lọc đối tác theo tiêu chí số di động
* Hỗ trợ lọc đối tác theo tiêu chí số điện thoại hoặc di động

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/res_partner_views.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
