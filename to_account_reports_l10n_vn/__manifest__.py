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

#. Provide the following financial reports for companies based in Vietnam in accordance with Vietnam Accounting Standard and requirements from the Ministry of Fiance

   * VAT Declaration
   * Profit and Loss (B02-DN)
   * Balance Sheet (B01-DN)
   * Cash Flow Statement (B03-DN)

#. Provide PDF and Excel version

   * Account detail sheet that is in compliance with the Circular No. 200/2014/TT-BTC dated 22 December 2014 of the Ministry of Finance of Vietnam
   * Accounting general ledger that is in compliance with the Circular No. 200/2014/TT-BTC dated 22 December 2014 of the Ministry of Finance of Vietnam
   * Account Bank/Cash book that is in compliance with the Circular No. 200/2014/TT-BTC dated 22 December 2014 of the Ministry of Finance of Vietnam

#. Provide Excel version

   * Invoicing and Bills Declaration that is in compliance with the Circular No. 200/2014/TT-BTC dated 22 December 2014 of the Ministry of Finance of Vietnam

Editions Supported
==================
1. Community Edition

    """,
    'description_vi_VN': """
Tính năng cơ bản
================

#. Cung cấp các báo cáo tài chính tương thích với chuẩn mực kế toán Việt Nam và các yêu cầu của Bộ Tài chính như sau

   * Tờ khai thuế giá trị gia tăng
   * Kết quả hoạt động kinh doanh (B02-DN)
   * Bảng Cân đối Kế toán (B01-DN)
   * Báo cáo Lưu chuyển Tiền tệ (B03-DN)

#. Cung cấp phiên bản PDF và Excel

   * Sổ chi tiết tài khoản tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính Việt Nam
   * Sổ sổ nhật ký chung tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính Việt Nam
   * Sổ quỹ tiền mặt và tiền gửi ngân hàng tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính Việt Nam

#. Cung cấp phiên bản Excel

   * Bảng sao kê hóa đơn, chứng từ hàng hóa, dịch vụ mua vào, bán ra theo mẫu ban hành kèm theo Thông tư số 119/2014/TT-BTC của Bộ Tài chính

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Localization',
    'version': '0.1.0',
    'depends': ['to_account_reports', 'l10n_vn_c200', 'l10n_vn_c133', 'to_account_counterpart', 'to_legal_invoice_number'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_tax_declaration_data.xml',
        'data/account_financial_report_data.xml',
        'data/profit_and_loss_line_data.xml',
        'data/cash_flow_statement_line_data.xml',
        'data/balance_sheet_line_data.xml',
        'data/account_financial_dynamic_report_line_data.xml',
        'data/account_financial_report_c133_data.xml',
        'data/balance_sheet_line_c133_data.xml',
        'data/profit_and_loss_line_c133_data.xml',
        'data/cash_flow_statement_line_data_c133.xml',
        'data/report_paperformat_data.xml',
        'views/report_financial_vn.xml',
        'views/account_chart_template_views.xml',
        'views/account_report_view.xml',
        'views/report_l10n_vn_s38dn.xml',
        'views/report_l10n_vn_s03adn.xml',
        'views/report_l10n_vn_s07dn.xml',
        'views/report_l10n_vn_s08dn.xml',
        'views/root_menu.xml',
        'wizards/l10n_vn_s38dn.xml',
        'wizards/l10n_vn_s03adn.xml',
        'wizards/l10n_vn_s07dn.xml',
        'wizards/l10n_vn_s08dn.xml',
        'wizards/l10n_vn_c119_01gtgt.xml',
        'wizards/l10n_vn_c119_02gtgt.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['to_account_reports', 'l10n_vn_c200', 'l10n_vn_c133'],
    'price': 999.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
