{
    'name' : 'PoS Analytics',
    'name_vi_VN' : 'Tài khoản quản trị trên PoS',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': 'PoS Analytics',
    'summary_vi_VN': 'Tài khoản quản trị trên PoS',
    'sequence': 30,
    'category': 'Accounting & Finance',
    'description':"""
What it does
============
This module helps define analytic account for each of Points of Sales

Key features
============
1. Automatically create a new analytic account upon a new Point of Sales creation. Such the auto creation option can be switched off on user choice
2. Automatically create analytic entries for Point of Sales Orders based on the account specified on the corresponding Point of Sales. The analytic entries are created upon closing the Point of Sales' sessions
3. During invoicing customers from Point of Sales screen, the analytic account of the Point of Sales will be set automatically on invoice lines.

Demo Video
----------

https://youtu.be/lloNrPX6zCs

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Mô tả
=====

Mô-đun này cho phép bạn chỉ định một tài khoản quản trị cho từng điểm bán hàng.

Tính năng nổi bật
=================
1. Tự động tạo một tài khoản quản trị mới khi tạo mới điểm bán hàng. Cho phép thiết lập tạo tự động hay không.
2. Dựa trên tài khoản được chỉ định cho từng điểm bán hàng, hệ thống sẽ tự động sinh ra các bút toán quản trị cho đơn đặt hàng PoS. Khi đóng phiên PoS, các bút toán này sẽ xuất hiện đồng loạt.
3. Trong quá trình lập hóa đơn cho khách hàng từ màn hình PoS, tài khoản quản trị của PoS sẽ được đặt tự động trên các dòng hóa đơn.

Demo Video
----------

https://youtu.be/lloNrPX6zCs

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['account', 'point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
