{
    'name': "Product Common UoM",
    'name_vi_VN': "Đơn vị tính chung của sản phẩm",
    'summary': """Add the Third UoM for products to be used in some cases""",
    'summary_vi_VN': """
Thêm Đơn vị tính (UoM) thứ ba để sản phẩm sử dụng trong một số trường hợp""",

    'description': """

Key Features
============

* Add the Third UoM for products to be used in some cases
* This module was built for other modules to extend

Supported Editions
==================

1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Tính năng nổi bật
=================

* Mô-đun này thêm đơn vị tính (UoM) thứ ba cho sản phẩm trong một số trường hợp
* Module này chỉ dùng cho module khác kế thừa

Ấn bản được hỗ trợ
==================

1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'views/product_template_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
