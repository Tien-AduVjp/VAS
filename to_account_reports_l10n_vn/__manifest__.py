# -*- coding: utf-8 -*-
{
    'name': "Accounting Reports - Vietnam Accounting",

    'name_vi_VN': "Báo cáo kế toán - Kế toán Việt Nam",

    'summary': """
Default template financial report for Vietnam""",

    'summary_vi_VN': """
Mẫu báo cáo tài chính mặc định dành cho các doanh nghiệp Việt Nam""",

    'description': """
Key Features
============
Provide the following financial reports for companies based in Vietnam in accordance
with Vietnam Accounting Standard and requirements from the Ministry of Fiance

* VAT Declaration
* Profit and Loss (B02-DN)
* Balance Sheet (B01-DN)
* Cash Flow Statement (B03-DN)

Editions Supported
==================
1. Community Edition
  
    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Cung cấp các báo cáo tài chính tương thích với chuẩn mực kế toán Việt Nam và các yêu cầu của Bộ Tài chính như sau

* Tờ khai thuế giá trị gia tăng
* Kết quả hoạt động kinh doanh (B02-DN)
* Bảng Cân đối Kế toán (B01-DN)
* Báo cáo Lưu chuyển Tiền tệ (B03-DN)
    
Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,
    
    'author': 'T.V.T Marine Automation (aka TVTMA)',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.1.3',

    # any module necessary for this one to work correctly
    'depends': ['to_account_reports', 'l10n_vn_c200', 'to_l10n_vn_qweb_layout'],

    # always loaded
    'data': [
        'data/account_tax_declaration_data.xml',
        'data/account_financial_report_data.xml',
        'data/profit_and_loss_line_data.xml',
        'data/cash_flow_statement_line_data.xml',
        'data/balance_sheet_line_data.xml',
        'data/account_financial_dynamic_report_line_data.xml',
        'views/report_financial_s200.xml',
        'views/account_chart_template_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['to_account_reports', 'l10n_vn_c200'],
    'price': 999.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
