{
    'name': "Vietnam - Overtime Payroll with Accounting",
    'name_vi_VN': "Việt Nam - Kế toán lương làm thêm giờ",

    'summary': """
Overtime Payroll & Vietnam Accounting Integration""",

    'summary_vi_VN': """
Kế toán lương Việt Nam cho tiền làm thêm giờ
    	""",

    'description': """
What it does
============
Integrate Overtime Payroll & Vietnam Accounting

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Tích hợp Bảng lương tăng ca với Kế toán Việt Nam

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_overtime_payroll', 'to_l10n_vn_hr_payroll_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],

    'images': [
    	'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
