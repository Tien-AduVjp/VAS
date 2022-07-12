
{
    'name': 'Product Quality',
    'name_vi_VN': 'Quản lý Chất lượng Sản phẩm',
    'summary': 'Quality Alerts and Control Points for Product',
    'summary_vi_VN': 'Cảnh báo chất lượng và Tiêu chí kiểm soát chất lượng cho Sản phẩm',

    'description': """

What it does
============
This module extends Quality app to manage quality for products.

Key Features
============
Manage quality points, quality checks and actions on each product.

Editions Supported
==================

1. Community
2. Enterprise

""",

    'description_vi_VN': """

Mô tả
=====
Module này mở rộng ứng dụng Quản lý Chất lượng để quản lý chất lượng sản phẩm.

Tính năng chính
===============
Quản lý tiêu chí kiểm soát chất lượng, kiểm tra chất lượng và các hành động trên mỗi sản phẩm.

Ấn bản được Hỗ trợ
==================

1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author' : 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Quality',
    'version': '0.1.0',
    'sequence': 50,

    'depends': ['to_quality', 'product'],
    'data': [
        'data/viin_quality_product_data.xml',
        'views/quality_alert_views.xml',
        'views/quality_check_views.xml',
        'views/quality_point_views.xml',
        'views/quality_alert_action_views.xml',
        'views/quality_alert_corrective_action_views.xml',
        'views/quality_alert_preventive_action_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
