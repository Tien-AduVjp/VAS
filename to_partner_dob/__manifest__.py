# -*- coding: utf-8 -*-
{
    'name': "Partner Date of Birth",
    'name_vi_VN': 'Ngày Sinh Của Đối Tác',
    'summary': """
Manage your partner's birthday""",
    'summary_vi_VN': """
Quản lý ngày sinh của đối tác""",
    'description': """
What it does
============
Manage your partners' birthday.

Key Features
============
* Manage Partner 's Birthday

    * Search/Filter Partners by:

        * Date of Birth
        * Day of Birth
        * Month of Birth
        * Year of Birth

    * Group Partners by:

        * Day of Birth
        * Month of Birth
        * Year of Birth

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Quản lý ngày sinh của đối tác.

Tính năng nổi bật
=================
* Quản lý Sinh nhật của Đối tác.

    * Tìm kiếm/ Lọc Đối tác theo:

        * Ngày tháng năm sinh
        * Ngày sinh
        * Tháng sinh
        * Năm sinh

    * Nhóm Đối tác theo:

        * Ngày sinh
        * Tháng sinh
        * Năm sinh

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['to_base'],

    # always loaded
    'data': [
        'views/res_partner_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
