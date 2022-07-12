{
    'name': "Expense - Employee Advance",
    'name_vi_VN': "Chi Tiêu - Tạm Ứng Nhân Viên",

    'summary': """
This module allows you to select employee if you choose employee edvance journal when payment expense""",

    'summary_vi_VN': """
Module này cho phép chọn nhân viên nếu chọn sổ tạm ứng nhân viên khi thanh toán chi tiêu
        """,

    'description': """
What it does
============
* When register payment for an expense invoice, you can choose payment methods by Cash Journal, Bank Journal, or Employee Advance Journal.
* In case you choose Employee Advance Jourrnal, you need to know exactly the used Journal belongs to which employee to reconcile the Expenses with the previous Advance.
* The module "Expenses - Employee Advances" will solve that.

Key Features
============
After installing this module:

* At the Regsiter Payment stage, when you select the "Employee Advance Journal" as  Payment method, an additional field *Employee* will display for you to choose from.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Khi thanh toán cho hóa đơn chi tiêu, bạn có thể lựa chọn phương thức thanh toán bằng Sổ Tiền mặt, Sổ Ngân hàng hoặc Sổ Tạm ứng Nhân viên.
* Trong trường hợp lựa chọn thanh toán bằng Sổ Tạm ứng Nhân viên, bạn cần biết chính xác là của nhân viên nào để phục vụ việc đối soát khoản Chi tiêu với khoản Tạm ứng trước đó.
* Mô-đun "Chi Tiêu - Tạm Ứng Nhân Viên" sẽ giải quyết điều đó.

Tính năng nổi bật
=================
Sau khi cài đặt mô-đun này:

* Tại bước Thanh toán, nếu chọn Phương thức thanh toán là "Sổ Tạm ứng nhân viên" sẽ xuất hiện thêm trường *Nhân viên* ở dưới để lựa chọn.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Accounting/Expenses',
    'version': '0.2.1',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_expense', 'to_hr_employee_advance'],

    # always loaded
    'data': [
        'views/hr_expense_sheet_views.xml',
        'wizard/account_advance_payment_register_views.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
