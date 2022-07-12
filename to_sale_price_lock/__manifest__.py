# -*- coding: utf-8 -*-
{
    'name': "Sales Price Lock",
    'name_vi_VN': "Khóa Giá Bán",
    'summary': """
Lock Sales Prices on sales quotation to salesmen (Users: own documents)""",
    'summary_vi_VN': """
Khóa giá bán đối trên báo giá với Người bán hàng (Người dùng: Chỉ tài liệu của chính mình)
""",
    'description': """
What it does
============
This is a simple application that locks the sales price in Sales Orders/Quotations against modification by Salespersons who are assigned into the groups "Users: own documents"

Key Features
============
* Allows to lock order/quote sales prices to prevent certain people from modifying them.
* Allows to change Sale Price Modifying Group in Sale Application Settings

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Đây là một ứng dụng đơn giản giúp khóa giá bán trên biểu mẫu Đơn bán/Báo giá để tránh bị sửa đổi bởi nhân viên bán hàng được phân vào nhóm "Người dùng: chỉ tài liệu của chính mình"

Tính năng nổi bật
=================
* Cho phép khóa giá bán đơn hàng/báo giá để ngăn một số người thuộc một nhóm nhất định sửa đổi.
* Cho phép thay đổi Nhóm sửa đổi giá bán trong phần Thiết lập của ứng dụng Bán hàng

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.0',

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    # any module necessary for this one to work correctly
    'depends': ['sale'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
