# -*- coding: utf-8 -*-
{
    'name': "SSH Keys Management",

    'summary': """Manage all your SSH Keys""",

    'description': """
Key Features
============
1. Manage SSH Keys
2. Check and Validate SSH Keys
3. SSH Keys are private and visible to their owning users and SSH Key Managers only. Users can add their own SSH Keys in user Preferences
4. Ready for others to extend

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
1. Quản lý SSH Keys
2. Kiểm tra và xác thực SSH Keys
3. SSH Keys là riêng tư và chỉ hiển thị cho người dùng sở hữu nó người Quản lý SSH Keys. Người dùng có thể thêm SSH Key của mình trong Hồ sơ cá nhân.
4. Là cơ sở để mở rộng cho các mô-đun khác

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.2.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'external_dependencies' : {
        'python' : ['paramiko'],
    },
    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/sshkey_pair_views.xml',
        'views/res_users_views.xml',
        'views/res_company_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
