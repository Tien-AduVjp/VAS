# -*- coding: utf-8 -*-
{
    'name': "Product Licenses",
    'name_vi_VN': "Giấy phép Sản phẩm",

    'summary': """
Manage licenses of your products""",
    'summary_vi_VN': """
Quản lý giấy phép sản phẩm của bạn""",

    'description': """
What it does
============
* The Product License module supports the creation and management of product licenses. A product can be assigned with one or more licenses.
* You can check the product license information in the Product Licenses module or in the Licenses tab of each product.

Key Features
============

1. Manage Licenses

   * You can define multiple licenses, each may have multiple versions. For example, LGPL v1, LGPL v3, AGPL v3, etc
   * You can define a short name (abbreviation) for a license.
   * Automatic showing first release date and latest release date.

2. Store different content for different versions of the license.
3. Assign Different License Versions to a product.
4. Filter products by license.
5. Filter products by license version.
6. Multilingual support so that you can translate the license content into as many languages as you may wish.
7. Some default data is available for you to use if suitable (Several types of licenses for the software industry):

   * GPL v3
   * AGPL v3
   * LGPL v3
   * OPL-1

8. Ready for other apps to integrate

   * Licensing your products sold with the **Product Licenses - Sales**: https://apps.odoo.com/apps/modules/12.0/to_product_license_sale/

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",

    'description_vi_VN': """
Mô tả
=====
* Mô đun Giấy phép sản phẩm hỗ trợ tạo và quản lý các giấy phép sản phẩm. Một sản phẩm có thể được gán với một hoặc nhiều giấy phép.
* Để kiểm tra các thông tin giấy phép sản phẩm, bạn có thể xem tại mô đun Giấy phép sản phẩm hoặc tab Licences của từng sản phẩm sau khi hoàn tất cài đặt mô đun này.

Tính năng nổi bật
=================
Mô đun này cho phép:

1. Quản lý giấy phép

   * Bạn có thể xác định nhiều giấy phép, mỗi giấy phép có thể có nhiều phiên bản. Ví dụ: LGPL v1, LGPL v3, AGPL v3, v.v.
   * Bạn có thể xác định tên viết tắt cho giấy phép.
   * Hiển thị ngày phát hành đầu tiên và ngày điều chỉnh gần nhất của từng giấy phép sản phẩm.

2. Lưu trữ nội dung thông tin khác nhau cho các phiên bản khác nhau của giấy phép.
3. Gán các phiên bản giấy phép khác nhau cho một sản phẩm.
4. Lọc sản phẩm theo giấy phép.
5. Lọc sản phẩm theo phiên bản giấy phép.
6. Hỗ trợ đa ngôn ngữ để bạn có thể dịch nội dung giấy phép sang nhiều ngôn ngữ tùy thích.
7. Có sẵn một số dữ liệu mặc định để bạn có thể sử dụng ngay nếu thấy phù hợp (Một số loại giấy phép cho ngành sản xuất phần mềm):

   * GPL v3
   * AGPL v3
   * LGPL v3
   * OPL-1

8. Sẵn sàng tích hợp với các ứng dụng khác:

   * Cấp phép cho các sản phẩm đã được bán của bạn với **Giấy phép Sản phẩm - Bán hàng**: https://apps.odoo.com/apps/modules/12.0/to_product_license_sale/

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com/apps/app/14.0/to_product_license',
    'support': 'apps.support@viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'data/license_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/product_license_views.xml',
        'views/product_license_version_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 45.9,
    'subscription_price': 3.31,
    'currency': 'EUR',
    'license': 'OPL-1',
}
