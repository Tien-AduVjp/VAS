{
    'name': "Product Milestone",
    'name_vi_VN': "Mốc Sản Phẩm",
    'summary': """
Manage product milestones that will be used in warranty, maintenance""",
    'summary_vi_VN': """
Quản lý các mốc hoạt động của sản phẩm, phục vụ cho việc bảo trì và bảo hành
    	""",
    'description': """
What it does
============
Manage product milestones that will be used in warranty, maintenance  

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Quản lý các mốc hoạt động của sản phẩm, phục vụ cho việc bảo trì và bảo hành 

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',

    'depends': ['uom'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_milestone_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
