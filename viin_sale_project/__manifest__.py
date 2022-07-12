{
    'name': "Sale Project",
    'name_vi_VN': "Bán hàng - Dự án",

    'summary': """
Grant project managers read access to the corresponding sales orders and sales order lines.""",

    'summary_vi_VN': """
Cho phép chủ nhiệm dự án có quyền đọc đơn bán và dòng đơn bán của dự án tương ứng
    	""",

    'description': """
Key Features
============
Grant project managers reading access to the sales orders and sales order lines to which the corresponding projects refer.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
Cấp quyền cho các chủ nhiệm dự án đọc đơn bán và dòng đơn bán mà có liên kết đến dự án của họ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_timesheet'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/module_security.xml',
        'views/project_project_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
