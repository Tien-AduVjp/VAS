{
    'name': "Product Maintenance Schedule",
    'name_vi_VN': "Lịch Bảo Trì Sản Phẩm",
    'summary': """
Define & Manage product maintenance Schedule based on product and product milestones""",

    'summary_vi_VN': """
Định nghĩa & Quản lý lịch bảo trì sản phẩm dựa theo sản phẩm và mốc hoạt động của sản phẩm
    	""",

    'description': """
What it does
============
This module manages maintenance operations based on equipment and equipment running time, that will help customer and operator know what to do, which part needs to replaced, what need to replace, what we need to prepare for maintenance  

Key Features
============
* New data list links to product manages all operations need to do based on product milestone
* In each operation, we can choose appropriate service and product to know what needs to do( check, clean or replace...)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này quản lý công việc chi tiết của việc bảo trì, sửa chữa dựa trên thiết bị và thời gian chạy của thiết bị. Việc này giúp khách hàng cũng như nhân viên bảo trì biết chi tiết cần làm những gì, cần thay thế những gì cũng như những linh kiện cần chuẩn bị 

Tính năng chính
===============
* Tạo ra bộ dữ liệu mới liên kết với sản phẩm để quản lý tất cả các công việc phải làm dựa trên mốc hoạt động của sản phẩm
* Trên mỗi công việc cụ thể, có thể chọn loại dịch vụ và sản phẩm phù hợp để biết việc phải làm( kiểm tra, vệ sinh hay thay thế ...)

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['product', 'to_product_milestone', 'maintenance'],

    # always loaded
    'data': [
        'security/maintenance_security.xml',
        'security/ir.model.access.csv',
        'views/product_maintenance_schedule_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
