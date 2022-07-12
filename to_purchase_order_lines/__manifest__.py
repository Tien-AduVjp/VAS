{
    'name': "Purchase Order Lines",
    'name_vi_VN': "Chi tiết đơn mua",
    'summary': """
Show Purchase order lines on the menu""",
    'summary_vi_VN': """
Hiển thị các dòng đơn mua trên menu""",
    'description': """
Show Purchase order lines under the Purchase menu entry

Key features
=============
This module helps show *Purchase Order lines* function on Orders menu of Purchase Management application

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=============

Hiển thị mục *Dòng đơn mua* trong menu Đơn mua của ứng dụng Quản lý Mua hàng

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Purchases',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_lines_views.xml',
         ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
