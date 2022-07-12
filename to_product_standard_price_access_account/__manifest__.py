{
    'name': "Product Standard Price Access - Accountant",
    'name_vi_VN': "Truy Cập Giá Vốn Sản Phẩm - Kế Toán",

    'summary': """
Grant accountants access to product Cost
       """,
    'summary_vi_VN': """
Cấp quyền cho Kế Toán viên truy cập vào Giá Vốn Sản Phẩm
        """,

    'description': """
Key Features
============
This module grants accountants access to the field Cost (also known as standard_price) on the product form view.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Module này cấp quyền cho kế toán viên truy cập vào trường Giá Vốn trên form Sản phẩm.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'to_product_standard_price_access'],

    # always loaded
    'data': [
        'security/product_standard_price_security.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
