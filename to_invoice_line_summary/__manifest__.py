# -*- coding: utf-8 -*-
{
    'name': "Invoice Lines Summary",
    'name_vi_VN': "Nhóm các dòng Hóa đơn",

    'summary': """Summary and group all Invoice's lines of the same Product into a new line in a new table""",
    'summary_vi_VN':"""Tổng hợp và nhóm các dòng của cùng một Sản phẩm trong Hóa đơn thành một dòng mới""",
    
    'description': """
Key Features
============

1. This application groups all the invoice's lines of the same product into a new line as the summarry. This is useful and may give ease of control when an invoice may contain many lines of the same product
2. A new PDF version of the invoice is additionally provided which is generated based on the summary lines. In other words, you can print a full version or summary version of an invoice

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============

1. Ứng dụng này nhóm tất cả các dòng của cùng một sản phẩm trong hóa đơn vào một dòng tổng hợp mới. Điều này sẽ hữu ích và giúp người dùng dễ dàng kiểm soát khi hóa đơn có nhiều dòng có cùng sản phẩm.
2. Một phiên bản PDF mới của hóa đơn sẽ được cung cấp thêm, phiên bản này được tạo ra dựa trên các dòng tổng hợp. Nói cách khác, bạn có thể in cả bản đầy đủ hoặc bản tổng hợp của hóa đơn.

Ấn bản hỗ trợ
==================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/report_invoice.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
