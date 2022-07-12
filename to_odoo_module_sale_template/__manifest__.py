{
    'name': "Odoo Apps Sales Template",
    'name_vi_VN': 'Mẫu báo giá ứng dụng Odoo',
    'old_technical_name': 'to_odoo_module_website_quote',
    'summary': "Quickly sell Odoo apps set using sales templates",
    'summary_vi_VN': 'Bán nhanh các ứng dụng Odoo bằng các biểu mẫu bán hàng',
    'description': """
What it does
============
In quotation templates, you can select the Odoo version and application category(ies), the system will automatically update the corresponding applications
to the quotation template instead of selecting applications one by one.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Khi tạo mẫu báo giá, bạn có thể lựa chọn phiên bản Odoo và nhóm ứng dụng mong muốn, hệ thống sẽ tự động cập nhật các ứng dụng tương ứng vào mẫu báo giá
thay vì phải lựa chọn từng ứng dụng một.

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Odoo Apps',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_odoo_module_sale', 'sale_quotation_builder'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_portal_template.xml',
        'views/sale_quote_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
