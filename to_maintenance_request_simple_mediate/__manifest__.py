{
    'name': "Form Maintenance Request Simple Extend",
    'name_vi_VN': "Mở Rộng Form Yêu Cầu Bảo Trì",
    'summary': """
Add div tag with class 'button_box' to the maintenance request form view
        """,

    'summary_vi_VN': """
Tạo thẻ HTML chứa các nút trên form yêu cầu bảo trì.
        """,

    'description': """
What it does
============
* Add div tag with class 'button_box' to the maintenance request form view for others to inherit and inject buttons inside

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Hiện tại trên form yêu cầu bảo trì chưa có nơi chứa các button
* Module này đơn giản chỉ thêm thẻ HTML vào form yêu cầu bảo trì để phục vụ các module về sau cho nhu cầu thêm button vào form này.

Ấn bản hỗ trợ
=============
1. Community
2. Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['maintenance'],

    # always loaded
    'data': [
        'views/maintenance_request_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
