{
    'name': "Fee Definition Sale Project",
    'name_vi_VN': "Phụ phí bán hàng - Dự án",

    'summary': """
Grant project managers read access to the corresponding sales order lines fee.""",

    'summary_vi_VN': """
Cho phép chủ nhiệm dự án có quyền đọc dòng phí đơn bán của dự án tương ứng
        """,

    'description': """
Key Features
============
Grant project managers reading access to the sales order lines fee to which the corresponding projects refer.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
Cấp quyền cho các chủ nhiệm dự án đọc dòng phí đơn bán mà có liên kết đến dự án của họ 

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
    'depends': ['viin_sale_project_technician','to_fee_definition_sale'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/module_security.xml', 
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
        # 'static/description/main_screenshot.png'
        ],
    'installable': False,
    'application': False,
    'auto_install': False, # set True after upgrading for v14
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
