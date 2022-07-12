# -*- coding: utf-8 -*-
{
    'name': "Website Apps Store",
    'name_vi_VN': 'Kho Ứng dụng Website',

    'summary': """
Running your own Odoo Apps Store""",
    'summary_vi_VN': """Vận hành Kho Ứng dụng Odoo của riêng bạn""",

    'description': """
What it does
============
- This module provides the feature to sell Odoo apps/modules developed by you in the App Store on your website. 
- You can optionally post the app/module product to the App Store.

Key Features
============
- Add Mega menu on your website to navigate to your App Store
- Add Add to cart button on product interface
- Navigate the Live Demo button to your demo link
- The module/app product is uploaded to the App Store by ticking the Generate App Product button in the Git application
- Module/app information is synced from manifest on github. You can also edit/add/delete these information on manifest

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    
     'description_vi_VN': """
Mô tả
=====
- Mô-đun này cung cấp tính năng bán ứng dụng/mô-đun Odoo do bạn phát triển trong Kho ứng dụng trên website của bạn.
- Bạn có thể tùy chọn sản phẩm ứng dụng/mô-đun được đưa lên Kho ứng dụng.

Tính năng nổi bật
=================
- Thêm Mega menu trên website của bạn để điều hướng đến Kho ứng dụng 
- Thêm nút Add to cart trên giao diện sản phẩm
- Điều hướng nút Live Demo đến đường link demo của bạn
- Sản phẩm mô-đun/ứng dụng được đưa lên Kho ứng dụng bằng cách tích chọn nút Tạo sản phẩm Ứng dụng trong ứng dụng Git
- Thông tin về mô-đun/ứng dụng được đồng bộ từ manifest trên github. Bạn cũng có thể sửa/thêm/xóa những thông tin này trên manifest

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'http://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_odoo_module_sale', 'website_sale'],

    # always loaded
    'data': [
        'data/product_attribute_data.xml',
        'data/product_public_category_data.xml',
        'data/website_pages_data.xml',
        'data/website_menu_data.xml',
        'views/git_branch_views.xml',
        'views/git_repository_views.xml',
        'views/res_config_settings_views.xml',
        'views/odoo_module_version_views.xml',
        # templates
        'views/cart_lines_template.xml',
        'views/continue_shopping_template.xml',
        'views/navbar_templates.xml',
        'views/template.xml',
        'views/website_sale_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'data/demo_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 999.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
