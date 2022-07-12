# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Validation",
    'name_vi_VN': "Thẩm định có mặt",

    'summary': """
Verify and compute HR attendance validity againts working schedule """,

    'summary_vi_VN': """
Thẩm định và Tính toán thời gian có mặt hợp lệ (theo lịch làm việc)
    	""",

    'description': """
Key Features
============

1. Automatic calculate late coming and early leave based on employee's contracted working schedule

   1. Late coming hours
   2. Early leave hours
   3. Total valid attendance hours (within contracted working schedule)

2. If enabled, aAutomatic fill missing check-out and mark the entry as "Auto-Checkout" for later tracking

   1. Missing check-out attendance entries will be automatically checked out after 10 hours counting from the time of expected valid checkout
   2. By default, this auto check-out schedule action (named `HR Attendance - Auto Checkout`) is disabled.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng chính
===============

1. Tự động tính toán đi muộn về sớm căn cứ theo lịch làm việc (thiết lập bởi hợp đồng nhân viên)

   1. Tổng số giờ đi muộn
   2. Tổng số giờ về sớm
   3. Tổng số giờ có mặt hợp lệ (theo lịch làm việc thiết lập trên hợp đồng)

2. Tự động điền giờ đăng xuất (ra) đối với những bản ghi có mặt mà nhân viên quên đăng xuất sau và đánh dấu "Tự động Đăng xuất" để tiện tra cứu sau này

   1. Tự động điền giờ đăng xuất (ra) đối với những bản ghi có mặt mà nhân viên quên đăng xuất sau 10 giờ kể từ giờ lẽ ra phải đăng xuất

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Attendances',
    'version': '0.1.3',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract', 'hr_attendance', 'viin_hr_employee_resource_calendar'],

    # always loaded
    'data': [
        'data/scheduler_data.xml',
        'views/hr_attendance_views.xml',
    ],

    'images': [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': ['hr_attendance', 'hr_contract'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
