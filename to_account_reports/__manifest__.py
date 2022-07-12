{
    'name' : 'Accounting Reports',
    'name_vi_VN' : 'Báo cáo kế toán',
    'summary': 'View and create reports',
    'summary_vi_VN': 'Xem và tạo các báo cáo kế toán',
    'version': '1.0.1',
    'category': 'Accounting',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'description': """
What it does
============
* Allows building reports based on the data-aggregated criteria according to some accounting rules
* Analyze real-time data, helping users summarize financial and accounting information promptly and quickly
* Provides managers with the overall financial picture to make decisions

Key features
============

* Creates real-time financial reports with criteria, Rules, how to collect data used for each criterion
* Creates financial reports including criteria with separate rules and data collection methods
* Compares data of different report types according to the selected period (week/month/year)
* Allows viewing data with some common report templates:

   #. GAAP Statements

     * Profit and Loss
     * Balance Sheet
     * Cash Flow Statement

   #. Management

     * Invoices
     * Analytic Report
     * Assets

   #. Partner Reports

     * Aged Receivable
     * Aged Payable
     * Partner Ledger

   #. Business Statements

     * Executive Summary

   #. Audit Reports

     * Tax Report
     * General Ledger
     * Trial Balance
     * Consolidated Journals

* Allows printing, downloading, exporting reports in PDF, EXCEL format

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Cho phép xây dựng báo báo dự trên các tiêu chí được tông hợp số liệu theo một số quy tắc kế toán
* Số liệu tập hợp theo thòi gian thực, giúp cho việc tổng hợp thông tin tài chính kế toán kịp thời, nhanh chóng
* Việc nắm bắt các số liệu và tiêu chính giúp các nhà quản lý, lãnh đạo doanh nghiệp có đầy đủ thông tin về bức tranh tài chính để ra quyết định

Tính năng nổi bật
=================
* Tạo báo cáo tài chính gồm nhiều tiêu chí, quy tắc, cách thức tập hợp dữ liệu sử dụng cho từng tiêu chí, từ các quy tắc trên tạo báo cáo tài chính theo thời gian thực
* So sách số liệu của các loại báo cáo theo chu kỳ lựa chọn (tuần/tháng/năm)
* Cho phép xem số liệu với một số mẫu báo cáo thông dụng:

   #. Báo cáo GAAP

     * Báo cáo kết quả HĐ Kinh doanh
     * Bảng cân đối kế toán
     * Báo cáo Lưu chuyển Tiền Tệ

   #. Quản lý

     * Hoá đơn
     * Báo cáo Quản trị
     * Tài sản

   #. Báo cáo Đối tác

     * Tuổi Nợ Phải thu
     * Tuổi Nợ Phải trả
     * Sổ cái Đối tác

   #. Báo cáo Kết quả Kinh doanh

     * Tóm tắt cho Quản lý

   #. Báo cáo Kiểm toán

     * Báo cáo Thuế
     * Sổ cái
     * Bảng cân đối phát sinh
     * Các Sổ nhật ký Hợp nhất

- Cho phép in, tải xuống, xuất file một số báo cáo the định dang PDF,EXCEL

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,
    'depends': ['to_enterprise_marks_account', 'to_account_financial_income', 'to_account_income_deduct', 'to_account_counterpart'],
    'data': [
        'security/ir.model.access.csv',
        'security/module_security.xml',
        'data/account_report_type.xml',
        'data/account_financial_dynamic_report_data.xml',
        'data/account_financial_dynamic_report_line_data.xml',
        'views/assets.xml',
        'views/account_report_views.xml',
        'views/report_financial.xml',
        'views/search_template_views.xml',
        'views/report_followup.xml',
        'views/partner_views.xml',
        'views/account_journal_dashboard_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_view.xml',
        'views/account_move_views.xml'
    ],
    'qweb': [
        'static/src/xml/account_report_template.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'auto_install': True,
    'installable': True,
    'application': False,
    'price': 1350.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
