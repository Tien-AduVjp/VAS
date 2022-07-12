{
    'name': "Track Changes in Reordering Rules",
    'name_vi_VN': 'Theo dõi lịch sử thay đổi Quy tắc tồn kho',
    'summary': """Add mail thread and track changes on Reordering Rules""",
    'summary_vi_VN': 'Thêm mail thread và theo dõi lịch sử thay đổi Quy tắc tồn kho',

    'description': """

What it does
============
- Modification of Reordering Rules (also known as min./max. stock rules) will affect your supply chain which may harm your business. Tracking changes (who did it, what the old value was, etc) could protect your business from unexpected changes.
- Normally, users with Admin access can modify the Reordering Rules. However, by default, these changes (who made it, how old the rule was, etc) are not logged. This module helps to log all changes made to Reordering Rules in the Chatter area.

Key Features
============
- Create the Chatter area in the Reordering Rule section
- Log all changes made to the Reordering Rule in the Chatter area: who changed it, the old - new value of the rule, when it was changed
- Allows users to communicate in the Chatter area

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
- Việc sửa đổi Quy tắc tái cung ứng (còn được gọi là quy tắc tồn kho tối thiểu/ tối đa) sẽ ảnh hưởng đến chuỗi cung ứng và có thể gây hại cho doanh nghiệp. Việc theo dõi các thay đổi trong Quy tắc tồn kho có thể bảo vệ doanh nghiệp khỏi những thay đổi bất ngờ ngoài ý muốn.
- Thông thường, người dùng có quyền Admin có thể thay đổi Quy tắc tồn kho. Tuy nhiên, hệ thống mặc định không ghi lại các thay đổi này (ai đã thực hiện, giá trị cũ của quy tắc là bao nhiêu, v.v). Mô-đun này giúp ghi lại lịch sử thay đổi Quy tắc tồn kho trong vùng Chatter.

Tính năng nổi bật
=================
- Tạo vùng Chatter trong mục Quy tắc tồn kho
- Ghi lại lịch sử thay đổi Quy tắc tồn kho trong vùng Chatter: ai là người thay đổi, giá trị cũ - mới của quy tắc là bao nhiêu, thay đổi vào thời gian nào
- Cho phép người dùng trao đổi trực tiếp trong vùng Chatter

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/warehouse_orderpoint_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
