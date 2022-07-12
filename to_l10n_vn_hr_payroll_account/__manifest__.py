{
    'name': "Vietnam - Payroll with Accounting",
    'name_vi_VN': "Tích hợp Bảng lương Việt Nam với kế toán",

    'summary': """Accounting Data for Vietnamese Payroll Rules""",
    'summary_vi_VN': """
Tích hợp Bảng lương Việt Nam với hệ thống tài khoản kế toán Việt Nam
      """,

    'description': """
What it does
============
This module is developed to help Vietnamese enterprises integrate Payroll with the Vietnamese Accounting System.

Key Features
============

#. Auto-Encoding payable and receivable into accounting system for each salary rule according to Vietnam Accounting Standard.
#. Set Accounts for salary rules according to Vietnam Accounting Standard. For example:

   * Basic Wage for Office Employee:

       * Debit Account: 642
       * Credit Account: 334

   * Basic Wage for Manufacturing Workers:

       * Debit Account: 627
       * Credit Account: 334

   * Travel Reimbursement for for Office Employee:

       * Debit Account: 642
       * Credit Account: 334

   * Travel Reimbursement for for Manufacturing Workers:

       * Debit Account: 627
       * Credit Account: 334

   * Etc.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

   """,

    'description_vi_VN': """
Mô tả
=====
Mô đun Tích hợp Bảng lương Việt Nam với kế toán được phát triển giúp người dùng sử dụng tích hợp Bảng lương Việt Nam với hệ thống tài khoản kế toán Việt Nam.

Tính năng nổi bật
=================

#. Tự động định khoản các khoản phải trả, phải thu vào hệ thống kế toán cho từng khoản lương theo Chuẩn mực Kế toán Việt Nam.
#. Định khoản các nguyên tắc tiền lương theo Chuẩn mực Kế toán Việt Nam. Ví dụ:

   * Mức lương cơ bản cho nhân viên văn phòng:

       * Nợ TK: 642
       * Có TK: 334

   * Mức lương cơ bản cho công nhân sản xuất:

       * Nợ TK: 627
       * Có TK: 334

   * Hoàn trả tiền đi lại cho nhân viên văn phòng:

       * Nợ TK: 642
       * Có TK: 334

   * Hoàn trả tiền đi lại cho Công nhân sản xuất:

       * Nợ TK: 627
       * Có TK: 334

   * v.v.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['to_l10n_vn_hr_payroll', 'l10n_vn', 'to_hr_payroll_account', 'viin_l10n_vn_hr_account'],

    # always loaded
    'data': [
    ],
    'images': ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['l10n_vn', 'to_hr_payroll_account'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
