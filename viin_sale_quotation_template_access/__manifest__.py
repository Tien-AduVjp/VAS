{
    'name': "Sales Quotation Template Access",
    'name_vi_VN': "Quyền truy cập mẫu báo giá",

    'summary': """
Define a group which granted quotation template access
""",
    'summary_vi_VN': """
Khởi tạo một nhóm được phân quyền truy cập mẫu báo giá
""",
    'description': """
Key Features
============
* Issue: Only users who belong to *Sales Administrator* group can access quotation template.
* This module defines a group which is granted access to quotation template.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
* Vấn đề: Chỉ người dùng thuộc nhóm *Sales Administrator* có thể truy cập mẫu báo giá.
* Module này khởi tạo một nhóm được phân quyền truy cập mẫu báo giá.

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    'author': "Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Sales',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_management'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/sale_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
