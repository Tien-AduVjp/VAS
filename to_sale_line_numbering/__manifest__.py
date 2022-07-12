{
    'name': "Sales Lines Numbering",
    'name_vi_VN': "Đánh số dòng Đơn bán",

    'summary': """
Enable Numbering on Sales Order Lines""",
    'summary_vi_VN': """
Cho phép đánh số trên các dòng Đơn bán
    """,
    'description': """
Key Features
============
This module shows lines numbering on Sales Order form and Sales Order/Quotation as PDF files, which helps display data orderly and comprehensively

Supported Editions
==================
1. Community Edition
2. Enterprise Edition


    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Mô-đun này hiển thị số thứ tự dòng đơn bán trên form nhập liệu và bản in PDF của đơn bán/báo giá, giúp hiển thị dữ liệu một cách có trật tự và dễ hiểu

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/sale_order_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
