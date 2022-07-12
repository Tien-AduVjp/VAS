{
    'name': "Equipment Image & Worksheet",
    'name_vi_VN': 'Hình ảnh và Bản vẽ Thiết bị',

    'summary': """
Add an image and a worksheet for an equipment""",
    'summary_vi_VN': """
Thêm hình ảnh và Bản vẽ cho một Thiết bị""",

    'description': """
Key Features
============
* Adding an image for an equipment. The image will be used on Kanban / Form views
* Adding a Worksheet (a PDF document) which is viewable and downloadable from the equipment form view. This is useful for storing equipment's manual/instruction

Supported Editions
==================
1. Community Edition
2. Enterprise Edition
    """,
    
     'description_vi_VN': """
Tính năng nổi bật
=================
* Thêm hình ảnh cho thiết bị bên trong giao diện form và hiển thị bên ngoài giao diện thẻ Kanban.
* Thêm trang Bản vẽ/Hướng dẫn để bạn có thể tải lên và xem nhanh tài liệu PDF liên quan đến thiết bị này (bản vẽ, sách hướng dẫn, v.v.) ngay trên giao diện Thiết bị. Tính năng này sẽ giúp bạn lưu trữ thông tin tập trung và dễ dàng tìm kiếm.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
""",

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['maintenance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/maintenance_equipment_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 19.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
