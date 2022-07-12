{
    'name': "Product Odoo Version",
    'name_vi_VN': "Biến thể sản phẩm theo phiên bản Odoo",
    'summary': """
Integrate Odoo Product with Odoo Version""",
    'summary_vi_VN': """
Tích hợp Sản phẩm với phiên bản Odoo""",
    'description': """
Key Features
============

This module supports management activities in selling Odoo applications

1. Create a new Odoo Version will automatically

   * Either create a new corresponding product attribute values if no value of the same name exists
   * Or map existing product attribute value of the same name

2. Create a new product attribute value of the Odoo Version attribute will automatically

    * Either create a new Odoo version and map with it if no Odoo version of the same name exists
    * Or map an existing Odoo version of the same name

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================

Mô-đun này hỗ trợ cho việc quản lý bán ứng dụng Odoo

1. Khi tạo mới một phiên bản Odoo, hệ thống sẽ tự động thực hiện một trong hai hành động sau:

    * Tạo mới một giá trị thuộc tính tương ứng cho sản phẩm nếu không có sẵn giá trị nào cùng tên với nó
    * Hoặc dẫn chiếu với giá trị thuộc tính cùng tên đã tồn tại

2. Khi tạo mới một giá trị thuộc tính của sản phẩm liên quan đến phiên bản Odoo, hệ thống sẽ tự động thực hiện một trong hai hành động sau:

    * Tạo mới một phiên bản Odoo và dẫn chiếu tới thuộc tính đó nếu không có phiên bản Odoo nào cùng tên đã tồn tại
    * Hoặc dẫn chiếu tới phiên bản Odoo cùng tên đã tồn tại


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
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_odoo_version', 'product'],

    # always loaded
    'data': [
        'data/product_attribute_data.xml',
        'data/odoo_version_data.xml',
        # 'security/ir.model.access.csv',
        'views/odoo_version_views.xml',
        'views/product_attribute_value_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
