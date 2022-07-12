{
    'name': "Inter-Company Rule for Invoices",
    'name_vi_VN': "Giao dịch liên công ty - Hóa đơn",
    'summary': """
Inter-Company Transactions for Invoices
        """,

    'summary_vi_VN': """
Giao dịch liên công ty cho hóa đơn (Bán hàng, mua hàng)
    	""",

    'description': """
What it does
============

* Conducing inter company transactions between 2 companies A and B in the same system

    * when validating an in invoice in company A, an out invoice will be auto created in company B
    * When validating an out invoice in company A, an in invoice will be auto created in company B
    * Also appling for refund invoices

Editions Supported
==================

1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Khi thực hiện giao dịch liên công ty giữa 2 công ty A và B trong hệ thống

    * Khi xác nhận hóa đơn bán hàng ở công ty A, hệ thống sẽ tự động tạo hóa đơn mua hàng ở công ty B
    * khi xác nhận hóa đơn mua hàng ở công ty A, hệ thống sẽ tự động tạo hóa đơn bán hàng ở công ty B
    * Áp dụng cả các hóa đơn hoàn trả

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
    'category': 'Productivity',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'to_inter_company_base'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
