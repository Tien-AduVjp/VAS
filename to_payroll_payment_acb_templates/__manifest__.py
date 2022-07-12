# -*- coding: utf-8 -*-
{
    'name': "Payroll Payment ACB Templates",
    'name_vi_VN': "Bảng chi hộ lương tháng theo mẫu ACB",

    'summary': """
When Confirm payroll, the Download button will appears.
""",

    'summary_vi_VN': """
Khi Xác nhận bảng lương thì xuất hiện nút Tải bảng Chi hộ lương ACB.
""",

    'description': """

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

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
    'category': 'Human Resources/Payroll',
    'version': '0.1',
    'depends': ['to_hr_payroll', 'to_base'],
    'data': [
        'views/hr_payslip_run_view.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
