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

This module provides additional filters to help you find some criteria more easily besides the default filters of Odoo

Key Features
============
#. Warehouse Dashboard, including:

   * Stock Report in graph view
   * Stock Report in cohort view

#. Show transfer addresses on map

#. KPI

   * Average Delivery Cycles Time
   * Average Receipt Cycles Time
   * Average Delivery Delay
   * Average Receipt Delay

#. Advanced filters in transfer list view to save user time on various inventory operations

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
===================
Cung cấp các tính năng nâng cao cho Kho tương tự như ở ấn bản Enterprise (với một vài khác biệt)

Cung cấp thêm các bộ lọc giúp bạn tìm kiếm một số tiêu chí dễ dàng hơn bên cạnh các bộ lọc mặc định của Odoo

Tính năng nổi bật
=================
#. Bảng thông tin Kho vận

   * Báo cáo kho dạng đồ thị
   * Báo cáo kho dạng bảng tổ hợp (cohort)

#. Hiển thị Địa chỉ giao nhận trên bản đồ

#. Các chỉ số đo lường hiệu suất

   * Thời gian giao hàng trung bình
   * Thời gian nhận hàng trung bình
   * Độ trễ giao hàng trung bình
   * Độ trễ nhận hàng trung bình

#. Các Bộ lọc nâng cao trong giao diện danh sách Dịch chuyển để tiết kiệm thời gian của người dùng trên nhiều hoạt động Kho

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo Technology Joint Stock Company",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'viin_web_map', 'viin_web_cohort', 'viin_web_dashboard'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'report/stock_report_views.xml',
        'views/stock_quant_views.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png',
        'static/description/warehouse_imp.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
