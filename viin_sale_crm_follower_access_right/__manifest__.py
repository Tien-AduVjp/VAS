{
    'name' : "Sales CRM Follower Access Rights",
    'name_vi_VN': "Quyền truy cập Bán hàng / CRM cho người theo dõi",

    'summary': "Allow followers to read and post message on lead/quotation/sales order",

    'summary_vi_VN': "Cho phép người theo dõi có thể truy cập đọc và đăng thông điệp ở tiềm năng/báo giá/đơn bán",

    'description':"""
Key Features
============
* When users are given the View their own documents only access, they are not allowed to access the documents of other users by default even though they have been added as followers 
* However, in reality, there are many cases where the coordination of a group of employees is needed, so they need to access relevant documents to view, exchange information and perform work (leads, opportunities, sales quotations, sales orders...)
* This module allows all employees who are added as followers to access documents even though they are not in charge of those documents.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Mặc định, khi được phân quyền chỉ xem tài liệu của chính mình, người dùng không được truy cập vào tất cả các tài liệu của người dùng khác phụ trách mặc dù được add follow.
* Trong thực tế, có rất nhiều trường hợp cần sự phối hợp của một nhóm nhân viên, chính vì vậy, họ cần truy cập vào tài liệu liên quan để xem thông tin và trao đổi, phối hợp thực hiện công việc (tiềm năng, cơ hội, báo giá, đơn hàng...)
* Mô-đun này cho phép tất cả nhân viên được add follow có thể truy cập tài liệu mặc dù không phải do mình phụ trách

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'Viindoo',
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 24,
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'crm'],

    # always loaded
    'data': [
        'security/module_security.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
