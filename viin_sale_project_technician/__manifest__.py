{
    'name': "Sale Project Technician",
    'name_vi_VN': "Bán hàng - Kỹ thuật viên dự án",

    'summary': """
Assign the Tech Lead for project and grant permission to read the sales order and sales order lines.""",

    'summary_vi_VN': """
Chọn một Kỹ Thuật Trưởng cho một dự án và cho phép đọc đơn bán và chi tiết đơn bán liên quan.""",

    'description': """
What it does
============
- Allow project manager to assign a user to be lead technician on a project. 
- Grant access to that lead technician to read the sales orders and sales order lines of the related project.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
- Cho phép chủ nhiệm dự án chỉ định một người dùng là kỹ thuật viên trưởng (Tech lead) phụ trách dự án.
- Cấp quyền cho Tech Lead đó được đọc đơn bán và dòng chi tiết đơn bán liên quan đến dự án đó.

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['viin_sale_project'],
    # always loaded
    'data': [
        'security/module_security.xml', 
        'views/project_task_views.xml'  
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
