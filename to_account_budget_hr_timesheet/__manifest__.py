{
    'name': "Account Budget Management - HR Timesheet",
    'name_vi_VN': 'Quản lý Ngân sách - Chấm công Nhân sự',
    'summary': """
Integrate HR Timesheet with Budgets Management""",

    'summary_vi_VN': """
Hỗ trợ tính chi phí timesheet ở ngân sách
    	""",

    'description': """
The problem
===========
By default in the module Account Budget Management (to_account_budget), only analytic lines that link with journal items
are included in budget's actual amount calculation when we apply Budgetary Positions. In case we have HR Timesheet installed,
the analytic lines created by timesheets may have no link to a journal item. Hence, these HR costs will not be considered in
the actual amount calculation.

The solution
============
This module adds a switch on budgetary positions to allow users to switch on the HR timesheet inclusion so that the timesheet costs
will affect the budget actual amount measurement as soon as they are entried.

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Vấn đề
======
Mặc định theo module Quản lý Ngân sách (to_account_budget), chỉ các phát sinh kế toán quản trị mà có liên kết với phát sinh kế toán
tài chính mới được xem xét trong việc tính toán và đo lường ngân sách khi chúng ta có sử dụng Kiểu Ngân sách. Trong trường họp chúng
ta sử dụng module Chấm công Nhân viên, các phát sinh kế toán quản trị ghi nhận bởi bảng chấm công sẽ không có liên kết với kế toán
tài chính và vì thế không được tính vào các ngân sách.

Giải pháp
=========
Module này bổ sung một tuỳ chọn ở Kiểu Ngân sách, cho phép người dùng có thể lựa chọn bao gồm chi phí công và đo lường ngân sách thực tế hay không

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_account_budget', 'hr_timesheet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_budget_post_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 49.5,
    'currency': 'EUR',
    'license': 'OPL-1',
}
