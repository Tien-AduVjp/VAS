{
    'name': "Vendor Price Lock",
    'name_vi_VN': 'Khóa Giá Của Nhà Cung Cấp',
    'summary': """Lock vendor pricelist, Lock Purchase Price on purchase order lines""",
    'summary_vi_VN': """Khóa bảng giá của nhà cung cấp, Khóa Giá Đơn mua trên chi tiết đơn mua""",
    'description': """
What it does
============
* This module allows purchase manager to lock vendor pricelist and lock purchase order line (shown in green) if vendor pricelist is locked.
* Once a vendor pricelist is locked, only purchase manager can unlock the pricelist.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
* Mô-đun này cho phép người quản lý đơn mua khóa bảng giá của nhà cung cấp và khóa chi tiết đơn đặt hàng (hiển thị bằng màu xanh lá cây) nếu bảng giá của nhà cung cấp bị khóa.
* Khi bảng giá của nhà cung cấp bị khóa, chỉ người quản lý đơn mua mới có thể mở khóa bảng giá.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition
    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'views/product_supplierinfo_views.xml',
        'views/purchase_order_line_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
