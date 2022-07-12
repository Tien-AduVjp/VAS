{
    'name': "Viin Sales",
    'name_vi_VN': "Viin Bán hàng",

    'summary': """
Advanced features for sales application
""",

    'summary_vi_VN': """
Các tính năng cao cấp cho ứng dụng bán hàng
""",

    'description': """
What it does
============
Advanced features for Sales application

Key Features
============
1. Sales Report

   * Days to confirm: new KPI to measure number of days from the date the order is created to the date the order is confirmed
   * Invoicing Status: new KPI for analyzing sales reports by invoice status

     * Upselling Opportunity
     * Fully Invoiced
     * To Invoice
     * Nothing to Invoice

2. Sales Report Dashboard which combines subviews of graph, pivot and cohort into a single view

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Các tính năng nâng cao trong ứng dụng Bán hàng

Tính năng chính
===============
1. Báo cáo bán hàng

   * Số ngày để xác nhận: chỉ tiêu mới để đo lường số ngày tính từ ngày tạo đơn đến ngày đơn được xác nhận
   * Tình trạng xuất hoá đơn: chỉ tiêu mới để phân tích báo cáo bán hàng theo tình trạng xuất hoá dơn

     * Cơ hội bán gia tăng
     * Đã xuất đủ hoá đơn
     * Chờ xuất hoá đơn
     * Không còn gì để xuất hoá đơn

2. Bảng tổng hơp báo cáo bán hàng chứa đồ thị pivot và phân tích tổ hợp (cohort) trên một giao diện duy nhất

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'viin_web_cohort', 'viin_web_dashboard'],
    'data': [
        'report/sale_report_views.xml',
        'views/sale_order_views.xml',
        'views/assets.xml',
    ],

    'images': [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
