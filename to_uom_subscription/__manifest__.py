{
    'name': "Subscription Unit of Measure",
    'name_vi_VN': "Nhóm đơn vị Thuê bao",

    'summary': """
New UoM type for subscription measurement""",

    'summary_vi_VN': """
Kiểu Đơn vị tính thời gian thuê bao
    	""",

    'description': """
Key Features
============
Create two new Units of Measure (UoM) Categories for Subscription measurement:

* Subscription: measured in hour(s), day(s), week(s), etc.
* User Subscription: measured in user/hour, user/day, user/week, etc.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Tạo mới hai nhóm Đơn vị tính với Kiểu đo lường là Thuê bao (tính tiền theo thời gian):

* Nhóm Thuê bao: đơn vị tính theo giờ, ngày, tháng, năm, v.v.
* Nhóm Thuê bao người dùng: đơn vị tính theo Người dùng/giờ, Người dùng/ngày, Người dùng/tháng, Người dùng/năm, v.v.

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
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['uom'],

    # always loaded
    'data': [
        'data/uom_data.xml',
        'views/uom_category_views.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
