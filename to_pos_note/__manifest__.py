{
    'name': 'PoS Order Note for Receipt Printing',
    'name_vi_VN': 'Ghi chú PoS cho việc in phiếu thu',
    'version': '1.0.0',
    'category': 'Point of Sale',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'sequence': 6,
    'summary': 'Enter notes on the PoS screen and print notes on the receipt',
    'summary_vi_VN': 'Nhập ghi chú trên màn hình PoS và in nó lên biên lai',
    'description': """
What it does
============

This module helps enter notes on the PoS screen and print PoS receipt with note.

Key features
============
1. PoS user, during order validation at PoS screen, can input some text as note into the PoS order
2. The note will be stored in the order and appear on the PoS Receipt.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Mô tả
=====
Mô-đun này giúp người dùng nhập ghi chú ngay trên màn hình PoS. Nội dung ghi chú sẽ hiển thị trên biên lai.

Tính năng nổi bật
=================
1. Trong quá trình xác thực tại màn hình PoS, nhân viên có thể nhập văn bản dưới dạng ghi chú.
2. Ghi chú sẽ được lưu lại và hiển thị trên biên lai.

Phiên bản hỗ trợ
================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_note_assets.xml',
    ],

    'qweb': ['static/src/xml/pos_note.xml'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
