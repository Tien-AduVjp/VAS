# -*- coding: utf-8 -*-
{
    'name': "Product Standard Price Access - Purchase User",
    'name_vi_VN': "Truy cập Giá Vốn Sản phẩm - Nhân viên Mua Hàng",
    
    'summary': """
Grant purchase users access to product Cost
       """,
    'summary_vi_VN': """
Cấp quyền truy cập cho nhân viên mua hàng vào Giá Vốn Sản phẩm
       """,
       
    'description': """
Key Features
============
This module grants purchase users access to the field Cost (also known as ```standard_price```) on the product form view.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Module này cấp quyền cho nhân viên mua hàng thấy trường Giá Vốn trên form Sản phẩm.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,


    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'to_product_standard_price_access'],

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
