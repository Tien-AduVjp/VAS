# -*- coding: utf-8 -*-
{
    'name': 'Account Balance Carry Forward',
    'name_vi_VN': 'Kết chuyển Số dư Tài khoản',

    'summary': """
Define account balance carry forward rules for automating account balance carry forward""",

    'summary_vi_VN': """
Thiết lập quy tắc kết chuyển số dư tự động để tự động hoá việc kết chuyển số dư các tài khoản
    """,

    'description': """
The problems
============
During closing periods (e.g. end of a fiscal year), reset account balance (carry the balance forward to the next period) for some accounts is a really heavy job. To get it done, accountants would need:

* To have good knowledge of their country's accounting standards on which accounts to be reset
* Calculate balance of the required accounts at the time of closing period. This also brings heavy workload to accountants and may get trouble by human errors

Key Features
============
#. Accounting Advisor / Manager can define account balance carry forward rules. For example,

    * 521 -> 511
    * 511 -> 911
    * etc.

#. Accountant can create a carry forward document which will automatically

    * load all the applicable rules
    * calculate the balance of all the source accounts, which will be carried forward to the next period for reviews

#. Upon validation of the document, Odoo will create accounting entries for each rule. It also respect the cummulative balance by ordering. For example,

    * Balance of the account 521: 100
    * Balance of the account 511: 550
    * The rules:

        * 521 -> 511
        * 511 -> 911

    * The result:

        * The First journal entry:

            * Debit 100 on 511
            * Credit 100 on 521

        * The Second journal entry:

            * Debit 450 (as the resul of 550-100) on 511
            * Credit 450 on 911

#. (new in Odoo 13): generate balance carry forward entries from selected journal items

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
'description_vi_VN': """
Vấn đề
======
Với tính năng hiện tại của Odoo khi kết thúc năm tài chính, chốt lại số dư tài khoản (chuyển số dư sang kỳ tiếp theo) đối với một số tài khoản là một công việc thực sự mất công sức. Để hoàn thành, các kế toán viên sẽ cần:

* Có kiến ​​thức tốt về các chuẩn mực kế toán của quốc gia mà trên đó các tài khoản được đặt lại
* Tính toán số dư của các tài khoản cần thiết tại thời điểm kết thúc năm tài chính. Điều này cũng mang lại khối lượng công việc rất lớn cho kế toán và không tránh khỏi nhầm lẫn khi thực hiện thủ công

Tính năng nổi bật
=================
#. Kế toán trưởng/ Kế toán viên có thể định nghĩa quy tắc kết chuyển số dư tài khoản. Ví dụ,

    * 521 -> 511
    * 511 -> 911
    * v.v.

#. Kế toán có thể tạo một bút toán kết chuyển tự động

    * Tải tất cả các quy tắc được áp dụng
    * Tính toán số dư của tất cả các tài khoản nguồn, sẽ được chuyển sang giai đoạn tiếp theo để xem xét

#. Khi xác nhận tài liệu, Odoo sẽ tạo các phát sinh kế toán cho từng quy tắc. Nó cũng nguyên tắc kết chuyển. Ví dụ,

    * Số dư tài khoản 521: 100
    * Số dư tài khoản 511: 550
    * Các quy tắc:

        * 521 -> 511
        * 511 -> 911

    * Kết quả:

        * Phát sinh đầu tiên:

            * Nợ 511: 100
            * Có 521: 100

        * Phát sinh thứ hai:

            * Nợ 211: 450 (là số tiền từ 550-100)
            * Có 911: 450

#. (mới ở Odoo 13): cho phép tạo bút toán kết chuyển từ các phát sinh kế toán được chọn.

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
    'category': 'Accounting',
    'version': '1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'data/sequence_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'wizard/account_balance_carry_forward_views.xml',
        'views/balance_carry_forward_rule_views.xml',
        'views/balance_carry_forward_rule_line_views.xml',
        'views/balance_carry_forward_views.xml',
        'views/account_move_line_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
