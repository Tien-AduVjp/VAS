{
    'name' : "Accounting Reports - Report Exclusion",
    'name_vi_VN' : 'Loại trừ bút toán khỏi Báo cáo Luật định',
    'summary': """
Excludes journal items that are marked with Excluded in Legal Reports from financial reports""",
    'summary_vi_VN': """
Loại bỏ khỏi báo cáo tài chính những phát sinh kế toán đã được đánh dấu là Loại bỏ khỏi Báo cáo Luật định""",

    'description': """
Key Features
============
- Allow users to Exclude entry from Legal Report
- At the same time, exclude the above entry from the financial statements

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

 """,
    
    'description_vi_VN': """
 Mô tả
======
- Cho phép lựa chọn loại trừ bút toán khỏi Báo cáo Luật định
- Đồng thời loại trừ bút toán được lựa chọn khỏi báo cáo tài chính

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA)',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_account_reports', 'to_accounting_entry_report_flag'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_financial.xml',
        'views/search_template_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'auto_install': True,
    'installable': True,
    'application': False,
    'price': 144.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
