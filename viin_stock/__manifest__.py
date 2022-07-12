{
    'name': "Viin Warehouse",
    'name_vi_VN': "Viin Kho Vận",

    'summary': """
Advanced Odoo EE like features for Warehouse
""",

    'summary_vi_VN': """
Các tình năng kho cao cấp tương tự Odoo EE
""",

    'description': """
What it does
============
This module provides the same advanced features for Warehouse as in the Enterprise edition (with some alternatives)

Key Features
============
1. Warehouse Dashboard, including:

   * Stock Report in graph view
   * Stock Report in cohort view

2. Show transfer addresses on map

3. KPI

   * Average Delivery Cycles Time
   * Average Receipt Cycles Time
   * Average Delivery Delay
   * Average Receipt Delay


Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
===================
Cung cấp các tính năng nâng cao cho Kho tương tự như ở ấn bản Enterprise (với một vài khác biệt)

Tính năng nổi bật
=================
1. Bảng thông tin Kho vận

   * Báo cáo kho dạng đồ thị
   * Báo cáo kho dạng bảng tổ hợp (cohort)

2. Hiển thị Địa chỉ giao nhận trên bản đồ

3. Các chỉ số đo lường hiệu suất

   * Thời gian giao hàng trung bình
   * Thời gian nhận hàng trung bình
   * Độ trễ giao hàng trung bình
   * Độ trễ nhận hàng trung bình

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo Technology Joint Stock Company",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'viin_web_map', 'viin_web_cohort', 'viin_web_dashboard'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_move_views.xml',
        'views/stock_picking_map_views.xml',
        'report/stock_report_views.xml',
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
