# -*- coding: utf-8 -*-
{
    'name': "Registration Email Blacklist",
    'name_vi_VN': "Danh sách đen Email đăng ký tài khoản",

    'summary': """
Define email blacklist to prevent blacklisted email account registration""",

    'summary_vi_VN': """
Thiết lập danh sách đen email để ngăn chặn đăng ký tài khoản bằng các email này
    	""",

    'description': """
What it does
============
This module allows administrator to define a list of blacklisted email rule to prevent users from registering an account using an email that matches a rule in the list.

Sample Rules
------------
#. *company.com*: this will block all the registration emails having the domain as *company.com*
#. *\*.company.com*: this will block all the registration emails having the domain as a subdomain of the *company.com*
#. *user@company.com*: this will block the registration email that exactly matches *user@company.com*
#. *\*user\*@\*.company.com*: this will block all the registration emails that contain *user* in their local partner and having the domain as a subdomain of the *company.com*
#. *company.\**: this will block all the registration emails that have the domain prefixed with *company.* and ended with any letters
#. *\*.company.\**: this will block all the registration emails that have *.company.* as a part of their domain name

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cho phép quản trị viên định nghĩa một danh sách các email danh sách đen để ngăn chặn người dùng đăng ký tài khoản sử dụng các email mà khớp với dánh sách đen này.

Các ví dụ
---------
#. *company.com*: sẽ chặn việc đăng ký bằng các email mà có tên miền là *company.com*
#. *\*.company.com*: sẽ chặn việc đăng ký bằng các email mà có tên miền là tên miền con của *company.com*
#. *user@company.com*: sẽ chặn việc đăng ký bằng các email mà khớp chính xác với *user@company.com*
#. *\*user\*@\*.company.com*: sẽ chặn việc đăng ký bằng các email mà chứa *user* ở phần trước @ và có tên miền là tên miền con của *company.com*
#. *company.\**: sẽ chặn việc đăng ký bằng các email mà có tên miền có tiên tố là *company.* và có hậu tố là bất kỳ ký tự nào
#. *\*.company.\**: sẽ chặn việc đăng ký bằng các email mà có tên miền có chứa *.company.*

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
    # Check https://github.com/tvtma/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['auth_signup'],

    # always loaded
    'data': [
        'data/block_reason_data.xml',
        'data/email.blacklist.rule.csv',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/block_reason_views.xml',
        'views/email_blacklist_rule_views.xml',
        'views/res_config_settings_views.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
