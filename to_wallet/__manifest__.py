{
    'name': "eWallet",
    'name_vi_VN': 'Ví điện tử',
    'summary': 'Deposit to eWallet of Commercial Partner',
    'summary_vi_VN': 'Nạp tiền vào ví đối tác',
    'description': """
What it does
============
* Record a payment to eWallet of partner. If the partner is a contact of a company, then it record to wallet of the company
* Support multi eWallet per currency
* Allow share eWallet for contacts in the same commercial partner
* Portal users can view and deposit to thier eWallets through a payment aquire.
* eWallet can be use to reconcile invoices

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
* Khi nhận một khoản thanh toán vào ví điện từ của đối tác. Nếu đối tác đó là cá nhân của một công ty thì số tiền sẽ được ghi nhận vào ví điện tử của công ty đó.
* Hỗ trợ đa tiền tệ. Mỗi tiền tệ là một ví điện tử tương ứng.
* Cho phép chia sẻ ví điện tử cho các cá nhân trong cùng một công ty.
* Người dùng portal có thể xem và nạp tiền vào ví thông qua các cổng thanh toán.
* Ví điện tử có thể được sử dụng để đối soát với các hóa đơn

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': ['payment',
                'to_payment_transaction_protection',
                'to_account_counterpart',
                'to_web_thousand_sep'
                ],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/account_invoice_views.xml',
        'views/account_move_line_views.xml',
        'views/account_payment_views.xml',
        'views/assets.xml',
        'views/payment_transaction_views.xml',
        'views/res_partner_views.xml',
        'views/wallet_portal_templates.xml',
        'views/wallet_views.xml'
    ],
    'qweb': [
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'images': [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 999.9,
    'subscription_price': 41.38,
    'currency': 'EUR',
    'license': 'OPL-1',
}
