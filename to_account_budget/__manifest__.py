# -*- coding: utf-8 -*-

{
    'name': 'Budget Management',
    'name_vi_VN': 'Ngân sách',
    'summary': """Use budgets to compare actual with expected revenues and costs""",
    'summary_vi_VN': """Sử dụng các ngân sách để so sách doanh thu và chi phí thực tế so với kế hoạch""",
    'category': 'Accounting/Budget',
    'author': 'Odoo S.A., T.V.T Marine Automation (aka TVTMA)',
    'description': """
What it does
============
Use budgets to compare costs against planned revenue

Key Features
===========
* Plan, propose and approve budgets
* Track budgets according to the related Analytics Accounts that have been planned
* Set budget types associated with different accounts which you want to track the related budget
* Budget management: track fluctuations from costs, revenue compared to the planned value

Editions Supported
==================
1. Community Edition

    """,
 
    'description_vi_VN': """
Mô tả
=====
Quản lý các khoản ngân sách: Chi phí, doanh thu thực tế so với kế hoạch từ đó giúp nhà Lãnh đạo doanh nghiệp có đầy đủ thông tin để đưa ra các quyết định.  

Tính năng nổi bật
=================
* Lập kế hoạch, đề xuất, phê duyệt ngân sách
* Cho phép thiết lập các Tài khoản quản trị 
* Cho phép theo dõi ngân sách theo các đầu Tài khoản quản trị liên quan đã được lên kế hoạch
* Cho phép thiết lập kiểu ngân sách gắn với nhiều tài khoản kế toán tài chính mà bạn muốn theo dõi ngân sách liên quan
* Quản lý ngân sách: theo dõi biến động từ chi phí, doanh thu so với giá trị trị kế hoạch

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community  

    """,
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'depends': ['to_enterprice_marks_account'],
    'data': [
        'security/account_budget_security.xml',
        'security/ir.model.access.csv',
        'views/to_account_budget_menu.xml',
        'views/account_analytic_account_views.xml',
        'views/crossovered_budget_views.xml',
        'views/account_budget_post_views.xml',
        'views/crossovered_budget_line_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'demo': ['data/account_budget_demo.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 189.9,
    'subscription_price': 9.44,
    'currency': 'EUR',
    'license': 'OPL-1',
}
