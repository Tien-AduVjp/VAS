# -*- coding: utf-8 -*-
{
    'name': "Vietnam - Payroll",
    'name_vi_VN': "Bảng lương Việt Nam",

    'summary': """Add Salary rules and structures according to Vietnam's nature""",
    'summary_vi_VN': """
Thêm quy tắc và cấu trúc lương theo đặc thù Việt Nam
    	""",
    
    'description': """
What it does
============
To set up salary rules and salary structure in Odoo, users need to know programming language and Python. This module pre-sets a number of rules according to Vietnam's nature. Users thereby can easily create the proper salary calculation for their business based on the available rules.

Key features
============
This module allows:

* Create Vietnamese specific salary rules:

  * Allowances
  * Insurance
  * Personal income tax
  * etc.

* Create groups of Vietnamese specific salary rules:

  * Basic salary group
  * Taxable/non-taxable allowance group
  * Deductions group
  * Taxable income group
  * Tax group
  * etc.

* Create basic salary structures for different job positions:

  * CEO salary
  * Manager salary
  * Salary of salesperson, accountants
  * etc.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Để thiết lập các quy tắc lương và cấu trúc lương trong Odoo, đòi hỏi người dùng cần biết ngôn ngữ lập trình và Python. Mô đun này thiết lập sẵn một số quy tắc theo đặc thù, cách tính lương của doanh nghiệp Việt. Từ đây, người dùng có thể sử dụng dễ dàng những quy tắc có sẵn để tạo ra cách tính toán lương phù hợp cho doanh nghiệp mình.

Tính năng nổi bật
=================
Mô đun này cho phép:

* Tạo ra các quy tắc lương đặc thù của Việt Nam:

  * Phụ cấp
  * Bảo hiểm
  * Thuế thu nhập cá nhân
  * v.v.

* Tạo ra các nhóm quy tắc lương đặc thù của Việt Nam:

  * Nhóm lương cơ bản
  * Nhóm phụ cấp tính thuế/ không tính thuế
  * Nhóm các khoản giảm trừ
  * Nhóm thu nhập chịu thuế
  * Nhóm thuế
  * v.v.

* Tạo một số cấu trúc lương cơ bản theo vị trí công việc:

  * Lương GĐ
  * Lương Quản lý
  * Lương NVKD, Kế toán
  * v.v.

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
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_payroll'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
