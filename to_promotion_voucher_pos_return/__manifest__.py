{
    'name' : 'Promotion Voucher - Goods Return in Point of Sales',
    'name_vi_VN':"Phiếu khuyến mãi - Trả lại hàng tại Điểm bán hàng",
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': '',
    'sequence': 30,
    'category': 'Point of sale',
    'description':"""
Summary
=======

This application integrated the application `Promotion Vouchers for Point of Sales` and
the application `Tracking PoS Return with Return Origin` to allow you take full control
of returning Point of Sales orders that were previously paid by promotion vouchers

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    
    'description_vi_VN': """
Tóm lược
========

Ứng dụng này tích hợp ứng dụng 'Phiếu khuyến mãi cho điểm bán hàng' và
ứng dụng 'Theo dõi đơn trả hàng từ đơn hàng gốc (POS)' để cho phép bạn toàn quyền kiểm soát
trả lại các đơn hàng của Điểm bán hàng đã được thanh toán trước đó bằng phiếu khuyến mãi 
    
Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    
    'depends': ['to_promotion_voucher_pos', 'to_pos_refund_origin'],
    'data': [
        'views/pos_order_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
