{
    'name': "Repair Order Delete",
    'name_vi_VN': "Xóa lệnh sửa chữa",

    'summary': """
Repair order delete""",

    'summary_vi_VN': """
Xóa lệnh sửa chữa""",

    'description': """
What it does
============
This module fixes bug can delete repair orders whose status is not draft or canceled
or have incurred accounting entries.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sửa lỗi có thể xóa lệnh sửa chữa có trạng thái không phải dự thảo hoặc đã hủy
hoặc đã phát sinh bút toán kế toán.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '0.1',

    'depends': ['repair'],
    'data': [
    ],
    'demo': [],
    'images' : [],
    'installable': True, # This module will be remove in version 14.0.
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
