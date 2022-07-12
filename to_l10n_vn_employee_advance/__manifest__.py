# -*- coding: utf-8 -*-
{
    'name': "Vietnam - Employee Advance",
    'name_vi_VN': 'Việt Nam - Tạm Ứng Nhân Viên',

    'summary': """Set defaut accounts according to the Vietnam accounting standards""",
    'summary_vi_VN': """Thiết lập tài khoản mặc định theo chuẩn mực kế toán Việt Nam""",

    'description': """

Key Features
============
* Upon installation of this module, all employee advance journals of the Vietnam chart of accounts will updated with 141 as the default account to meet VAS requirements.
* Allow to print general voucher in case journal of payment was Employee Advance Journal.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Tính năng nổi bật
=================
* Sau khi module này được cài đặt, tất cả các sổ tạm ứng nhân viên trong hệ thống tài khoản Việt Nam được cập nhật với tài khoản tạm ứng 141 mặc định để đáp ứng chuẩn mực kế toán Việt Nam
* Cho phép in phiếu kế toán trong trường hợp thanh toán đó nằm trong sổ nhật ký *Tạm ứng*.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_employee_advance', 'l10n_vn', 'to_print_payment_vi'],
    'data':[
        'data/journal_data.xml',
        'views/report_general_voucher_views.xml',
        'views/report.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
