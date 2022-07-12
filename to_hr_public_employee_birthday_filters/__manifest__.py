# -*- coding: utf-8 -*-
{
    'name': "Public Employee Birthday Filters",
    'name_vi_VN': "Tìm kiếm Danh bạ Nhân viên theo Ngày sinh",
    'summary': """
Search / Filter employees with birthday criteria
        """,
    'summary_vi_VN': """
Tìm kiếm / Lọc Nhân viên theo tiêu chí ngày sinh
         """,
    'description': """
Key Features
============

Search Employees by Birthday critetia
-------------------------------------
1. Search employees by day of birth. For example, find ones who were born on day 5, etc
2. Search employees by month of birth. For example, find ones who were born in May, etc
3. Search employees by year of birth. For example, find ones who were born in 1980, etc

Predefined Filters
------------------
* Birthday this week
* Birthday last week
* Birthday next week
* Birthday this month
* Birthday last month
* Birthday next month

    """,
     'description_vi_VN': """
Các tính năng chính
===================

Tìm kiếm Nhân viên thông qua tiêu chí ngày sinh
-----------------------------------------------
1. Tìm kiếm nhân viên thông qua ngày sinh. Ví dụ, tìm các nhân viên sinh vào ngày mùng 5, ...
2. Tìm kiếm nhân viên thông qua tháng sinh. Ví dụ, tìm các nhân viên sinh vào tháng 5, ...
3. Tìm kiếm nhân viên thông qua năm sinh. Ví dụ, tìm các nhân viên sinh vào năm 1980, ...

Bộ lọc được Xác định trước
--------------------------
* Sinh nhật trong tuần này
* Sinh nhật trong tuần trước
* Sinh nhật trong tuần tới
* Sinh nhật trong tháng này
* Sinh nhật trong tháng trước
* Sinh nhật trong tháng tới

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_employee_birthday_filters'],

    # always loaded
    'data': [
        'views/hr_public_employee_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',

}
