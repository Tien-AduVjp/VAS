{
    'name': "Overtime Approval Payroll",
    'name_vi_VN': "Tích hợp Phê duyệt Tăng ca vào Phiếu lương",


    'summary': """
Technical module that bridges Overtime and Approval and Payroll""",

    'summary_vi_VN': """
Mô-đun kỹ thuật làm cầu nối tích hợp các mô-đun Tăng ca, Phê duyệt, Tiền lương
    	""",

    'description': """

Key Features
============
* This module is to integrate the Overtime, Approval and Payroll applications
* The overtime data which are approved will be sent and calculated in Payroll

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """

Tính năng nổi bật
=================
* Mô-đun này giúp kết nối các ứng dụng Tăng ca, Phê duyệt và Bảng lương với nhau.
* Dữ liệu tăng ca khi được phê duyệt sẽ được chuyển đến và tính toán trong ứng dụng Bảng lương

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_overtime_payroll', 'viin_hr_overtime_approval'],

    # always loaded
    'data': [
        'views/hr_payslip_views.xml',
    ],

    'images': [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 27.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
