{
    'name': "Stock Equipment",
    'name_vi_VN': "Thiết Bị Và Kho",
    'summary': """
Integrate Equipment with Inventory application for equipment stock and tracing""",
    'summary_vi_VN': """
Tích hợp quản lý Kho với Thiết bị để lưu trữ và truy xuất nguồn gốc""",
    'description': """
The problem
===========
By default, Odoo does not offer any relation between stockable goods and equipments. These are totally independent objects. From an equipment view, we do NOT know where the equipment comes from.

Solution
========
This module allows equipments generated automatically from a stock-in transfer. In other words, if a product is marked with "Can be equipment", during receving the product, Odoo will generate equipments according to the product quantity so that you can maintain the product later on using maintenance application. When looking at an equipment, you will also know from where it came and how it has moved so far.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Đặt vấn đề
==========
Theo mặc định, Odoo không cung cấp bất kỳ mối quan hệ nào giữa sản phẩm có thể lưu kho và thiết bị. Đây là những đối tượng hoàn toàn độc lập. Từ góc nhìn thiết bị, chúng ta KHÔNG biết thiết bị đến từ đâu.

Giải pháp
=========
Mô-đun này cho phép các thiết bị được tạo tự động từ dịch chuyển kho. Nói cách khác, nếu một sản phẩm được đánh dấu là "Có thể là thiết bị", trong quá trình nhận sản phẩm, Odoo sẽ tạo ra các thiết bị theo số lượng sản phẩm để bạn có thể bảo trì sản phẩm sau này khi sử dụng ứng dụng Bảo trì. Khi nhìn vào một thiết bị, bạn cũng sẽ biết nó đến từ đâu và nó đã di chuyển như thế nào cho đến nay.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['hr_maintenance', 'stock'],

    # always loaded
    'data': [
        'data/res_config_settings.xml',
        'data/stock_picking_type.xml',
        'views/stock_move_line_views.xml',
        'views/stock_production_lot_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/product_views.xml',
        'views/product_category_views.xml',
        'views/stock_picking_type_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
