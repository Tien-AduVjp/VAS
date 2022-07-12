# -*- coding: utf-8 -*-
{
    'name': "Return in Point of Sales Screen",
    'name_vi_VN': "Trả hàng ngay trên màn hình PoS",
    'summary': """
Return orders in PoS Screen
         """,
    'summary_vn_VN': """
Đơn trả hàng ngay tại màn hình PoS
         """,

    'description': """
The problem
===========

By default, when a customer of yours comes to return the goods she or he bought from you, you would need to

1. Get rid off the PoS screen and navigate to the Point of Sales order list in the backend to find the corresponding order.
2. After validation, you need to open that order in the backend and do return.

There is nothing wrong here but not so productive and waste your time.
If you usually process hundred orders per session which may get you tired,
doing more tasks may lead to some human errors.
    
The solution
============

Instead of going to the backend interface, you keep stay at the PoS screen and do lookup for the order to return then carry out the return process. It's quick and more easier!

Key Features
============

1. Pos Manager can set maximum number of days for goods return in case your company does not accept goods return after a period counting from the date of purchase.
2. PoS users can do return process while staying in the same screen.
3. PoS users will get notified if the return is not within the allowed return period.
4. Keep track of the return thanks to the features offer by the application *PoS Refund Origin* which is a dependency of this application.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Vấn đề
======

Theo mặc định, khi một khách hàng của bạn đến trả hàng mà họ đã mua từ bạn, bạn cần phải:

1. Thoát khỏi màn hình PoS và điều hướng đến danh sách đơn hàng trong phần phụ trợ để tìm đơn hàng tương ứng.
2. Sau khi xác thực, bạn cần mở thứ tự đơn hàng đó và thực hiện trả hàng.

Không có gì sai ở đây nhưng nó không hiệu quả và lãng phí thời gian của bạn.
Nếu bạn xử lý hàng trăm đơn hàng mỗi phiên, nó có thể khiến bạn mệt mỏi, nhiều tác vụ hơn có thể dẫn đến lỗi của con người.
    
Giải pháp
=========

Thay vì phải thoát khỏi màn hình PoS, bạn tiếp tục ở lại và tìm kiếm đơn hàng, sau đó thực hiện quy trình trả hàng. Thật nhanh chóng và dễ dàng hơn!

Tính năng nổi bật
=================

1. Người quản lý có thể đặt số ngày tối đa cho việc trả lại hàng hóa trong trường hợp công ty của bạn không chấp nhận trả lại hàng sau một khoảng thời gian kể từ ngày mua hàng.
2. Người dùng PoS có thể hoàn trả đơn hàng trong khi vẫn ở cùng một màn hình.
3. Người dùng PoS sẽ được thông báo nếu đơn hàng không nằm trong khoảng thời gian cho phép.
4. Theo dõi đơn hàng hoàn trả nhờ các tính năng được cung cấp bởi ứng dụng *PoS Refund Origin*, một phụ thuộc của ứng dụng này.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_pos_refund_origin'],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/product_view.xml',
        'views/pos_config_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
