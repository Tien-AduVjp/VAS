{
    'name': 'Promotion Voucher - Accounting Payment',
    'name_vi_VN': "Phiếu khuyến mãi - Kế toán thanh toán ",
    'version': '1.0.0',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': '',
    'summary_vi_VN': '',
    'sequence': 30,
    'category': 'Sales',
    'description': """
Summary
=======

Integrates Promotion Voucher application with Payment and Accounting for customers to pay the goods
they buy from you using promotion vouchers

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tổng quan
=========

Tích hợp ứng dụng Phiếu khuyến mãi với Thanh toán và Kế toán để khách hàng thanh toán tiền hàng
họ mua từ bạn bằng cách sử dụng phiếu khuyến mãi
    
Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    'depends': ['to_promotion_voucher'],
    'data': [
        'views/account_payment_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
