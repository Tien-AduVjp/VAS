{
    'name' : 'Promotion Vouchers for Point of Sales',
    'name_vi_VN':"Phiếu khuyến mãi cho điểm bán hàng ",
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': '',
    'summary_vi_VN': '',
    'sequence': 30,
    'category': 'Point of sale',
    'description':"""
Summary
=======

Integrates Promotion Voucher application with Point of Sales application, so that

1. You can sell vouchers at your Points of Sales
2. Customers at your Points of Sales can pay you using their promotion vouchers (which they bought / were given away before)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tóm lược
========

Tích hợp ứng dụng Phiếu khuyến mãi với ứng dụng Điểm bán hàng, để

1. Bạn có thể bán phiếu khuyến mãi tại Điểm bán hàng của mình
2. Khách hàng tại Điểm bán hàng của bạn có thể thanh toán cho bạn bằng phiếu khuyến mãi của họ (họ đã mua / được tặng trước đó)

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    'depends': ['to_promotion_voucher', 'point_of_sale'],
    'data': [
        'data/menu.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/account_move_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
