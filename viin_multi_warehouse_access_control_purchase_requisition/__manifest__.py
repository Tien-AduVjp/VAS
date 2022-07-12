{
    'name': "Multi-Warehouse Access Control - Purchase Requisition",
    'name_vi_VN': "Kiểm Soát Truy Cập Đa Kho - Hợp đồng mua hàng",

    'summary': """
Integrate Multi-Warehouse Access Control with Purchase Requisition.""",
    'summary_vi_VN': """
Tích hợp Kiểm soát truy cập Đa Kho với Hợp đồng mua hàng.""",

    'description': """
What it does
============
Bridge module between Multi-Warehouse Access Control and Purchase Agreements modules.

Key Features
============
    * Get default operation type when creating new purchase agreement by the warehouses that user can access.
    
Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Module cầu nối giữa module Kiểm soát truy cập đa kho với Hợp đồng mua hàng.

Tính năng nổi bật
=================
    * Lấy hoạt động kho mặc định khi tạo mới hợp đồng mua hàng theo kho mà người dùng đó có thể truy cập.
    
Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Warehouse',
    'version': '0.1.0',
    'depends': ['to_multi_warehouse_access_control_purchase', 'purchase_requisition'],

    'data': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
