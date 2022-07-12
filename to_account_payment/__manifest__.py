{
    'name': "Payment with Payment Lines",
    'name_vi_VN': "Thanh toán với các dòng thanh toán",
    'summary': """Payment with multiple payment lines for different countered accounts""",
    'summary_vi_VN': """Thanh toán với các dòng thanh toán để đối ứng thanh toán với nhiều tài khoản""",

    'description': """
The problem
===========

Currently, when making a payment, the countered journal item of the bank/cash move is recorded with the payable
or receivable account specified on the corresponding payment's partner. It was impossible for the user to record
a payment that is countered with multiple accounts. Here was impossible s for example

+----+---------------------+-------+--------+
| ID | Account             | Debit | Credit |
+----+---------------------+-------+--------+
|  1 | Bank/Cash           |   150 |      0 |
+----+---------------------+-------+--------+
|  2 | Another Receivable1 |     0 |    100 |
+----+---------------------+-------+--------+
|  3 | Another Receivable2 |     0 |     50 |
+----+---------------------+-------+--------+


Solution
========

This module was developed to extend payment mechanism in Odoo to allow users to a payment lines for a payment on which different
reconcilable accounts (not just limited to payable/receivable ones) to fullfil the requirement of the above mentioned situation

This module also offers a tool on payment form view to allow users to load residual amount summary of each reconcilable account
of the corresponding partner for convenient instead of manually calculation of residual amount that they have to pay or receive.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Vấn đề
======

Hiện tại Odoo có ba hình thức thanh toán:

    * Nhận tiền:

        * Nợ: Tài khoản tiền mặt (ngân hàng)
        * Có: Tài khoản phải thu

    * Gửi tiền:

        * Nợ: Tài khoản phải trả
        * Có: Tài khoản tiền mặt (ngân hàng)

Người dùng không thể tạo nhiều dòng phải trả hoặc phải thu trong một khoản thanh toán.

Giải pháp
=========

Mô-đun này được phát triển để mở rộng Thanh toán trong Odoo:

    * Khi người dùng chọn hình thức thanh toán là Nhận tiền hoặc Gửi tiền bằng Thanh toán, hệ thống sẽ cho phép họ nhập các dòng phải trả hoặc phải thu trong bảng Chi tiết thanh toán
    với các tài khoản và số tiền có thể tùy chỉnh.

        * Nếu Chi tiết thanh toán không được thêm bất kỳ dòng nào vào, Odoo sẽ sử dụng các tài khoản mặc định của Odoo để sinh bút toán, ví dụ:

            * [1] Nợ (Tài khoản phải trả): $100
            * [2] Có (Tiền mặt): $100

        * Nếu các dòng Chi tiết thanh toán được thêm vào, Odoo sẽ căn cứ vào các dòng chi tiết thanh toán để sinh bút toán, ví dụ:

            * [1] Nợ (Tài khoản phải trả 1): $ 50
            * [2] Nợ (Tài khoản phải trả 2): $ 30
            * [3] Nợ (Tài khoản phải trả 3): $ 20
            * [5] Có (Tiền mặt): $100

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_payment_mediate', 'viin_account_reconciliation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
        'views/account_payment_line_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
