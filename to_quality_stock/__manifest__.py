{
    'name': "Stock Quality Control",
    'name_vi_VN': 'Kiểm soát Chất lượng Kho',
    'summary': """Quality Control for your in, out, internal stock moves""",
    'summary_vi_VN': """Kiểm soát chất lượng cho các dịch chuyển kho (nhập, xuất, nội bộ)""",
    'description': """
Key Features
============

* Define quality points that will generate quality checks on pickings,
  manufacturing orders or work orders (when to_quality_mrp is installed)
* Quality alerts can be created independently or related to quality checks
* Define and manage Alert Actions (corrective actions, preventive actions) on each and every Quality Alert
* Possibility to add a measure to the quality check with a min/max tolerance
* Define your stages for the quality alerts
* Analyse Quality Action
* SPC reports

Editions Supported
==================

1. Community
2. Enterprise, with prior removal the of Enterprise Edition's Quality application

    """,
'description_vi_VN': """
Tính năng chính
===============

* Xác định các tiêu chí kiểm soát chất lượng sẽ tạo ra kiểm tra chất lượng trên các giao nhận,
   đơn hàng sản xuất hoặc hoạt động sản xuất (khi to_quality_mrp được cài đặt)
* Cảnh báo chất lượng có thể được tạo độc lập hoặc liên quan đến kiểm tra chất lượng
* Xác định và quản lý Hành động cảnh báo (hành động khắc phục, hành động phòng ngừa) trên mỗi và mọi Cảnh báo chất lượng
* Khả năng thêm đo lường vào kiểm tra chất lượng với dung sai tối thiểu/tối đa
* Xác định các giai đoạn của bạn cho các cảnh báo chất lượng
* Phân tích hành động chất lượng
* Báo cáo SPC

Phiên bản hỗ trợ
================

1. Community Edition
2. Enterprise Edition, nhưng phải gỡ ứng dụng Chất lượng của ấn bản Enterprise trước.

    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Operations/Quality Control',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'viin_quality_product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/module_security.xml',
        'views/root_menu.xml',
        'views/quality_alert_views.xml',
        'views/quality_check_views.xml',
        'views/quality_point_views.xml',
        'views/quality_alert_action_views.xml',
        'views/stock_picking_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/quality_demo.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
