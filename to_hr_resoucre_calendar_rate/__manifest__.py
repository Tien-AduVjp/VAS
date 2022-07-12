# -*- coding: utf-8 -*-
{
    'name': "HR Resoucre Calendar Rate",
    'name_vi_VN': 'Tỉ lệ theo giờ làm việc',
    'summary': """
Add rate in percentage to Resource Calendar Atteandance""",
    'summary_vi_VN': """
Thêm tỉ lệ phần trăm theo giờ làm việc
""",
    'description': """
This module adds a new field 'Rate' to Resource Calendar Attendance for usage in other modules (e.g. Payroll for differenciate work hours rates)

    """,
    'description_vi_VN': """
Module này bổ sung thêm trường 'Tỷ lệ (%)' theo mỗi Giờ làm việc để các module khác sử dụng lại (ví dụ: Tính lương theo tỷ lệ giờ làm việc khác nhau)

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['resource'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/resource_calendar_attendance_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
