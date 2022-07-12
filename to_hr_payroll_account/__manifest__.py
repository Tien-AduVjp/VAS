{
    'name': 'TVTMA HR Payroll Accounting',
    'name_vi_VN': "Kế toán lương",
    
    'summary': """
Allows the entire Payroll Accounting to be automatically calculated through pre-established rules""",

    'summary_vi_VN': """
Giúp toàn bộ nghiệp vụ Kế toán lương trong doanh nghiệp được định khoản tự động
    	""",

    'description': """
What it does 
============
In large-scale enterprises, the process of payroll accounting is quite time-consuming and prone to errors. Viindoo's Payroll Accounting module allows the entire Payroll Accounting to be automatically calculated through pre-established rules.

Key Features
============
* Set up accounting rules related to payroll accounting:

  * On salary rules
  * On the Labor Contract

* When the payslip is confirmed, the entries are automatically created and recorded in the relevant accounting journals.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Đối với doanh nghiệp có số lượng nhân viên lớn, quá trình thực hiện nghiệp vụ hạch toán lương khá tốn thời gian và dễ xảy ra nhiều sai sót. Mô đun Kế toán lương của Viindoo giúp toàn bộ nghiệp vụ Kế toán lương trong doanh nghiệp được định khoản tự động thông qua các quy tắc đã được thiết lập sẵn.

Tính năng nổi bật
=================

* Thiết lập quy tắc kế toán liên quan đến nghiệp vụ kế toán lương:

  * Trên quy tắc lương
  * Trên Hợp đồng Lao động

* Thời điểm phiếu lương được xác nhận, các bút toán được tự động tạo và ghi nhận vào sổ kế toán liên quan.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    
    'category': 'Human Resources/Payroll',
    'version': '1.1.2',
    'author': 'Odoo SA,T.V.T Marine Automation (aka TVTMA)',
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'maintainer': 'T.V.T Marine Automation (aka TVTMA)',
    'depends': ['to_hr_payroll', 'account', 'viin_hr_account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_line_views.xml',
        'views/account_move_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payroll_structure_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_payslip_views.xml',
        'views/res_config_settings_views.xml',
        ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['to_hr_payroll', 'account'],
    'price': 0.0,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
