{
    'name': "Loan Management",
    'name_vi_VN': "Vay & Cho Vay",

    'summary': """
Manage your company loans""",
    'summary_vi_VN': """
Quản lý các khoản vay của công ty bạn""",

    'description': """
Key Features
============
The total solution for Managing and tracking all kinds of company loans with less effort

#. Borrowing Loan Contracts

    * Borrowing Loan Disbursements: Automatic Planning and Tracking
    * Borrowing Loan Refunds: Automatic Planning and Tracking
    * Borrowing Loan Interests: Forecast and tracking

#. Lending Loan Contracts

    * Lending Loan Disbursements: Automatic Planning and Tracking
    * Lending Loan Refunds: Automatic Planning and Tracking
    * Lending Loan Interests: Forecast and tracking

#. Automatic Loan Interest computation which supports both fixed interest rate and floating interest rate
#. Fully integrated with Accounting

    * Auto journal entries encoding for loan disbusements
    * Auto journal entries encoding for loan principal refunds
    * Invoicing/billing multiple loan interests with one click
    * Pay loan interests to the borrowers and reconcile with loan interest bills
    * Get paid for loan interest from lenders and reconcile with loan interest invoices

#. Fully integrated with Analytics Accounting

    * Auto analytics entries that also link to general accounting journal items
    * Analytics tags support

#. Rich reports to help you get full insight of your loan activities and transactions
#. Multi-Currency Support
#. Multi-Company Support

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Giải pháp tổng thể để quản lý và theo dõi tất cả các loại vay/cho vay của công ty một cách đơn giản

#. Hợp đồng vay

    * Giải ngân khoản vay: Lập kế hoạch và theo dõi tự động
    * Hoàn trả tiền gốc: Lập kế hoạch và theo dõi tự động
    * Lãi suất: Dự báo và theo dõi lãi suất

#. Hợp đồng cho vay

    * Giải ngân khoản cho vay: Lập kế hoạch và theo dõi tự động
    * Hoàn trả tiền gốc: Lập kế hoạch và theo dõi tự động
    * Lãi suất cho vay: Dự báo và theo dõi lãi suất cho vay

#. Tính toán lãi suất cho vay tự động, hỗ trợ cả lãi suất cố định và lãi suất thả nổi.
#. Tích hợp đầy đủ với kế toán

    * Tự động sinh các bút toán kế toán cho các khoản vay/cho vay
    * Tư động sinh các bút toán kế toán cho hoàn trả khoản vay gốc
    * Lập hóa đơn/thanh toán nhiều khoản vay với một click
    * Thanh toán tiền lãi cho người vay và đối chiếu với hóa đơn lãi vay
    * Được thanh toán tiền lãi cho vay từ người vay và đối chiếu với hóa đơn lãi vay

#. Tích hợp đầy đủ với Kế toán Quản trị

    * Các bút toán kế toán quản trị tự động cũng được liên kết đến các phát sinh kế toán tổng hợp
    * Hỗ trợ các thẻ tài khoản quản trị

#. Báo cáo đầy đủ để để giúp bạn hiểu rõ hơn về hoạt động và giao dịch vay/cho vay của bạn
#. Hỗ trợ đa tiền tệ
#. Hỗ trợ đa công ty

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com/intro/loan-management",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1.3',

    # any module necessary for this one to work correctly
    'depends': ['account', 'to_base'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'data/product_category_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/loan_management_product.xml',

        'wizard/interest_invoicing_wizard_views.xml',

        'wizard/loan_disbursement_payment_wizard_view.xml',
        'wizard/loan_refund_payment_wizard_view.xml',

        'views/account_chart_template_views.xml',
        'views/loan_interest_rate_type.xml',

        # Loan setting
        'views/res_config_settings.xml',

        # Loan Order Views
        'views/abstract_loan_order_views.xml',
        'views/loan_borrowing_order_view.xml',
        'views/loan_lending_order_view.xml',

        # Loan Disbursement Views
        'views/abstract_loan_disbursement_views.xml',
        'views/loan_borrow_disbursement_views.xml',
        'views/loan_lend_disbursement_views.xml',

        # Loan Refund Views
        'views/abstract_loan_refund_line_views.xml',
        'views/loan_borrow_refund_line_views.xml',
        'views/loan_lend_refund_line_views.xml',

        # Loan Interest Views
        'views/abstract_loan_interest_line_views.xml',
        'views/loan_borrow_interest_line_views.xml',
        'views/loan_lend_interest_line_views.xml',

        # Loan Payment Views
        'views/abstract_loan_payment_views.xml',
        'views/loan_disbursement_payment_views.xml',
        'views/loan_refund_payment_views.xml',

        # Loan reports
        'views/loan_report_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 249.9,
    'subscription_price': 14.07,
    'currency': 'EUR',
    'license': 'OPL-1',
}
