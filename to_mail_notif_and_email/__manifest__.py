{
    'name': "Inbox Notifications and Emails",
    'name_vi_VN': 'Thông Báo Hệ Thống Và Email',
    'summary': """
Notifications to both the Odoo Inbox and Email""",
    'summary_vi_VN': """
Các thông báo sẽ xuất hiện trong cả Hộp thư đến của Odoo và Email của bạn""",
    'description': """
The Problem
===========
By default, Odoo provides two options for Notification Management:

* Handle by Emails: notifications are sent to the users' email. This is the default option for new user creation
* Handle in Odoo: notifications appear in the users' Odoo Inbox but no email sent to the users

This module does the following
------------------------------

**Handle by Emails** now offers both inbox and email notifications

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Đặt vấn đề
==========
Theo mặc định, Odoo cung cấp hai tùy chọn cho Quản lý thông báo:

* Xử lý bằng email: thông báo được gửi đến email của người dùng. Đây là tùy chọn mặc định để tạo người dùng mới
* Xử lý trong Odoo: thông báo xuất hiện trong Hộp thư đến Odoo của người dùng nhưng không có email nào được gửi đến người dùng

Mô-đun này làm gì
-----------------
** Xử lý bằng email ** hiện cung cấp cả thông báo hộp thư đến và email

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Discuss',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['mail'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
