# -*- coding: utf-8 -*-
{
    'name': "Employee Birthday Filters",
    'name_vi_VN': "Tìm kiếm Nhân viên theo Ngày sinh",
    'summary': """
Search / Filter employees with birthday criteria
        """,
    'summary_vi_VN': """
Tìm kiếm / Lọc Nhân viên theo tiêu chí ngày sinh
         """,
    'description': """
What it does
============
* "Employee Birthday Filters" module was developed to support employees searches by date of birth.

Key Features
============
* Search Employees by Birthday critetia

        * Search employees by day of birth. For example, find ones who were born on day 5, etc.
        * Search employees by month of birth. For example, find ones who were born in May, etc.
        * Search employees by year of birth. For example, find ones who were born in 1980, etc.

* Predefined Filters

        * Birthday this week
        * Birthday last week
        * Birthday next week
        * Birthday this month
        * Birthday last month
        * Birthday next month

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Mô đun "Tìm kiếm Nhân viên theo Ngày sinh" được phát triển hỗ trợ tìm kiếm nhân viên theo tiêu chí ngày/tháng/năm sinh.

Tính năng nổi bật
=================
* Tìm kiếm Nhân viên thông qua tiêu chí ngày sinh

        * Tìm kiếm nhân viên thông qua ngày sinh. Ví dụ, tìm các nhân viên sinh vào ngày mùng 5, ...
        * Tìm kiếm nhân viên thông qua tháng sinh. Ví dụ, tìm các nhân viên sinh vào tháng 5, ...
        * Tìm kiếm nhân viên thông qua năm sinh. Ví dụ, tìm các nhân viên sinh vào năm 1980, ...

* Bộ lọc được Xác định trước

        * Sinh nhật trong tuần này
        * Sinh nhật trong tuần trước
        * Sinh nhật trong tuần tới
        * Sinh nhật trong tháng này
        * Sinh nhật trong tháng trước
        * Sinh nhật trong tháng tới

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
    'category': 'Human Resources',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'to_partner_dob'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',

}
