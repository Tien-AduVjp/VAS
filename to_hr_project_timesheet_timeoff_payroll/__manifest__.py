# -*- coding: utf-8 -*-
{
    'name': "Exclude Time off Timesheet records on Payslip",
    'name_vi_VN': "Loại trừ bản ghi chấm công Nghỉ trên Phiếu lương",

    'summary': """
On payslip, exclude timesheet records that represent time off on payslip
""",

    'summary_vi_VN': """
Trên phiếu lương, loại trừ các bản ghi chấm công đại diện cho thời gian nghỉ
        """,

    'description': """
What it does
============
When linking payslip with timesheet records, exclude timesheet records that represent time off

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Khi liên kết phiếu lương với các bản ghi chấm công, loại trừ các bản ghi chấm công đại diện cho thời gian nghỉ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_timesheet_payroll', 'project_timesheet_holidays','viin_project_timesheet_leave'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
