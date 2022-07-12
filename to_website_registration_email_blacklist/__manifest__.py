{
    'name': "Website Account Registration Email Blacklist",
    'name_vi_VN': "Danh sách đen email đăng ký tài khoản ở website",

    'summary': """
Website and Registration Email Blacklist Integration""",

    'summary_vi_VN': """
Tích hợp Website với Danh sách đen Email đăng ký tài khoản
    	""",

    'description': """
What it does
============
Allow access quickly to Email Blacklist and Block Reason in website setting view

Key Features
============
- Prevent user account registration with blacklisted email
- Allow access quickly to Email Blacklist and Block Reason in website setting view

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
    
Mô tả
=====
- Module cho phép Quản trị viên đặt ra các quy tắc để đưa email vào danh sách đen. 

Tính năng nổi bật
=================
- Chặn người dùng đăng ký tài khoản bằng email trong danh sách đen
- Cho phép truy cập nhanh vào danh sách đen email và lý do chặn thông qua giao diện cài đặt website

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
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['to_registration_email_blacklist','website'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
