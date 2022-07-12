{
    'name': "Employee Advance",
    'name_vi_VN': "Tạm ứng Nhân viên",
    'summary': """
Employee Advance requests and approval""",
    'summary_vi_VN': """
Yêu cầu và phê duyệt tạm ứng của nhân viên""",
    'description': """
What it does
============
Employee Advance is an module for Odoo that allows you to manage employee advance.

* Employee can create requests for advance payment
* The Employee Manager and the Module Manager can approve/reject the request
* Accounting Department can then carry out payments according to the approved advance requests
* The Employee Advance will be reconciled with the expense form Employee advance Journal
* At the end of a period, accountants can reconcile all those transactions above

Key Features
============
* Manage advance payment process: Draft > Waiting Approved > Approved > Done > Reconciled
* Employee can request one or multiple request
* Allow Employee Advance Double Validation if advance amount greater than the value to be set
* Integrated with Expense and Accounting Entry

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun Tạm Ứng Nhân Viên cho phép bạn quản lý tạm ứng của nhân viên với quy trình tạm ứng đơn giản:

* Nhân viên tạo yêu cầu thanh toán tạm ứng
* Quản lý nhân viên và Quản lý Mô-đun có thể phê duyệt/từ chối yêu cầu
* Kế toán thực hiện thanh toán theo yêu cầu tạm ứng đã được phê duyệt
* Khoản tạm ứng của nhân viên sẽ được đối soát với khoản chi tiêu từ Sổ Nhật ký Tạm ứng của chính nhân viên đó.
* Vào cuối chu kỳ kế toán, kế toán viên có thể đối soát tất cả các giao dịch trên.

Tính năng nổi bật
=================
* Quản lý Quy trình tạm ứng: Đề nghị tạm ứng > Chờ duyệt > Đã phê quyệt > Đã thanh toán > Đã đối soát
* Tạo và Gửi nhiều yêu cầu tạm ứng
* Cho phép thẩm định Tạm ứng nhân viên 2 lần nếu số tiền tạm ứng lớn hơn so với giá trị được thiết lập
* Được tích hợp với mô-đun Chi tiêu và Kế toán

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com/intro/employee-advance",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Human Resources/Advance',
    'version': '1.0.5',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_account'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'wizards/employee_advance_payment_views.xml',
        'wizards/employee_advance_reconcile_batch_views.xml',
        'wizards/account_advance_payment_register_views.xml',
        'views/employee_advance_views.xml',
        'views/employee_advance_reconcile_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_payment_views.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
