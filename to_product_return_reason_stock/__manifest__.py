# -*- coding: utf-8 -*-

{
    'name' : 'Product Return Reasons - Inventory',
    'name_vi_VN': 'Lý Do Trả Hàng - Hàng Tồn Kho',
    
    'summary': 'Specify a reason during stock return',
    'summary_vi_VN': 'Chỉ ra lý do trả về kho',
    
    'description':"""
Key Features
============

1. Users can defined unique Product Return Reasons
2. Inventory Managers can set 'Return Reason Required' for a specific Return Operation so that Product Returns
   of that operation always required inventory users to specify a reason during return processing
3. Analyze Stock Moves by Return Reasons
4. Analyze Stock Pickings by Return Reasons

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính Năng
=========

1. Người dùng có thể định nghĩa lý do trả lại hàng
2. Quản lý kho có thể chỉ định 'Cần Lý Do Trả Lại' cho hành động trả lại để khi sản phẩm bị trả lại
   người dùng phải nêu lý do vì sao sản phẩm đó bị trả lại
3. Phân tích dịch chuyển kho theo lý do trả hàng
4. Phân tích giao nhận hàng theo lý do trả hàng

Ấn bản hỗ trợ
==================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    
    'version': '1.0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'sequence': 30,
    'category': 'Warehouse',
    'depends': ['to_product_return_reason', 'stock'],
    'data': [
        'security/module_security.xml',
        'views/menu.xml',
        'views/stock_picking_view.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_type_views.xml',
        'views/return_picking_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
