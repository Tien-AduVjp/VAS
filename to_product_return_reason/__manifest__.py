{
    'name' : 'Product Return Reasons',
    'name_vi_VN': 'Lý do trả hàng',

    'summary': 'Base application for product return reasons management',
    'summary_vi_VN': 'Ứng dụng cơ sở cho việc quản lý lý do trả hàng',

    'description':"""
Summary
=======

This technical module offers a new model for users to define return reason. A return reason consists of the following information:

1. Name: The name of the Return Reason, for example: Bad quality, Customer changed mind, etc
2. Description: Description of the reason

NOTES
-----
This module does nothing. It aims to provide the base for other applications to extend. See

* Stock Return Reasons: https://apps.odoo.com/apps/modules/13.0/to_product_return_reason_stock/
* Point of Sales Return Reasons: https://apps.odoo.com/apps/modules/13.0/to_product_return_reason_pos/

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tổng quan
=========

Đây là module kỹ thuật tạo ra một model mới để định nghĩa các lý do trả hàng. Một lý do trả hàng bao gồm các thông tin sau:

1. Tên: Tên của lý do trả hàng, ví dụ: Chất lượng kém, khách hàng đổi ý, v.v
2. Mô tả: Mô tả lý do

Chú ý
-----

Module này không làm gì. Nó nhằm mục đính cung cấp thông tin cơ sở cho ứng dụng khác mở rộng. Xem

* Lý Do Trả Lại Kho: https://apps.odoo.com/apps/modules/13.0/to_product_return_reason_stock/
* Lý Do Trả Hàng Điểm Bán Lẻ: https://apps.odoo.com/apps/modules/13.0/to_product_return_reason_pos/

Ấn bản hỗ trợ
==================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'sequence': 30,
    'category': 'Sales',
    'depends': ['product'],
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/products_return_reason.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
