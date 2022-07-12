{
    'name': 'Master Production Schedule',
    'name_vi_VN': 'Kế hoạch Sản xuất Tổng thể',
    'summary': 'Master Production Scheduling with forecast',
    'summary_vi_VN': 'Lập Kế hoạch Sản xuất Tổng thể theo dự báo',
    'description': """
What it does
============
* Sometimes you need to create the purchase orders for the components of manufacturing orders that will only be created later, or for production orders where you will only have the sale orders later.
* This module plans sales forecast to proactively create and purchase and manufacturing orders in advance to satisfy production demand.

Key Features
============
- Allow users to choose the products to add to the report
- Allow users to choose the reporting period: day, week, month, etc.
- Define safety stock, maximum/minimum quantity to supply and change the quantity to purchase
- Allow manual override of the quantity to be purchased

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
* Đôi khi bạn cần tạo đơn mua nguyên vật liệu, thiết bị... sau khi có lệnh sản xuất hoặc đơn sản xuất được tạo sau khi có đơn bán.
* Mô-đun này sẽ lập kế hoạch dự báo bán hàng để chủ động tạo trước đơn sản xuất và đơn mua hàng cho phù hợp với nhu cầu sản xuất.

Tính năng nổi bật
=================
- Cho phép tùy chọn các sản phẩm muốn thêm vào báo cáo
- Cho phép chọn khoảng thời gian báo cáo: ngày, tuần, tháng, ...
- Định nghĩa mức tồn kho an toàn, tối đa/tối thiểu để cung cấp và thay đổi số lượng định mua
- Cho phép ghi đè thủ công số lượng sẽ mua

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Manufacturing',
    'version': '1.1',

    'depends': ['to_enterprise_marks_mrp', 'purchase_stock'],

    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/mrp_mps_templates.xml',
        'views/mrp_production_schedule_views.xml',
        'views/stock_move_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/mrp_mps_forecast_details_views.xml'
    ],

    'demo': [
        'data/mps_demo.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': ['static/src/xml/templates.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 450.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
