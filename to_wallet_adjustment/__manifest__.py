# -*- coding: utf-8 -*-
{
    'name': "eWallet Adjustment",
    'name_vi_VN': "Điều chỉnh ví điện tử",

    'summary': """Adjust wallet payment amount
""",

    'summary_vi_VN': """Điều chỉnh số dư trong ví
""",

    'description': """
What it does
============
Allowing your customers to deposit and make transaction by e-wallet, you'd need to adjust the amount in your customer's wallet, e.g. enter the opening amount, give an reward amount etc)
This module helps you to make that adjustment without creating payment transactions

Key features
============
* By default, the wallet amount can only be adjusted using a payment entry.
* Installing this module, you can create amount adjustment entries and they will be stored and linked on the wallet management form in your Accounting application.
* *For example*: Adjust to increase wallet amount: Debit 811/Credit 131. Adjust to decrease wallet amount: Debit 131/Credit 711.
* Payable or Receivable account could be set on Customer form. Income or Expenditure account could be set on Wallet Adjustment Journal.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Khi khách hàng của bạn nạp tiền và thanh toán bằng ví điện tử, trong một số trường hợp, bạn cần điều chỉnh số dư trong ví của khách hàng, ví dụ: nhập số tiền đầu kỳ
Mô-đun này giúp bạn thực hiện việc điều chỉnh đó mà không thông qua các giao dịch thanh toán

Tính năng nổi bật
=================
* Theo mặc định, chỉ có thể điều chỉnh số dư trong ví bằng bút toán thanh toán.
* Với mô-đun này, bạn có thể tạo các bút toán điều chỉnh số dư và chúng sẽ được lưu lại trên giao diện quản lý Ví Khách hàng trong ứng dụng Kế toán của bạn. 
* *Ví dụ*: Điều chỉnh tăng tiền trong ví, hệ thống sẽ ghi nhận: Nợ 811/Có 131. Điều chỉnh giảm, hệ thống sẽ ghi nhận: Nợ 131/Có 711. 
* Có thể thiết lập tài khoản phải thu/phải trả trên form khách hàng, tài khoản Doanh thu/Chi phí trên Sổ nhật ký Điều chỉnh Ví.

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['to_wallet'],

    # always loaded
    'data': [
        'wizard/wallet_adjust_views.xml',
        'views/wallet_views.xml'
    ],

    'post_init_hook': 'post_init_hook',

    'images': [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
