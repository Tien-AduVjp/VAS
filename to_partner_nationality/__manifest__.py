{
    'name': "Partner Nationality Management",
    'name_vi_VN': 'Quản Lý Quốc Tịch Đối Tác',
    'summary': """
Manage Partner Nationality""",
    'summary_vi_VN': """
Quản lý quốc tịch đối tác""",
    'description': """
Key Features
=============
* Add Partner nationality field on the Contact form.
* Search Contacts by nationality.
* Manage partner nationality.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
==================
* Thêm trường Quốc tịch đối tác trên hồ sơ Liên hệ.
* Tìm kiếm Liên hệ theo quốc tịch.
* Quản lý quốc tịch đối tác.

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
    'depends': ['mail'],

    # always loaded
    'data': [        
        'views/res_partner_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
