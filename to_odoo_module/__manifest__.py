# -*- coding: utf-8 -*-
{
    'name': "Odoo Apps",
    'name_vi_VN': 'Odoo Apps',

    'summary': """
Manage Odoo apps / modules. Generate apps from a git branch""",
    'summary_vi_VN': 'Quản lý ứng dụng / module Odoo. Tự tạo ứng dụng từ nhánh git',

    'description': """
Features at a glance
====================

1. Define and Manage Odoo Modules with multiple versions against Odoo versions
2. Integrated with Odoo's products
3. Integrated with Invoicing for manage billing and payments regarding to your module sales
4. Integrated with Git Management application to allow

   * Add git branches that contains your Odoo Apps/Modules
   * Scan the branches for automatic Odoo Apps / Modules discovering
   * Schedule automatic branches scanning periodically

5. Synchronize modules data with Products

   * Automatically created new products or map with the existing ones identified by product code and module technical name matching
   * Mapp Odoo Versions with Product Attributes
   * Automatic update products images, price, vendor price, product licenses (thanks to the integration with the Product License Management application), etc

6. Customer Portal Apps Downloads

   * Customer can login to your portal and download the Apps that she or he bought either

     * from the invoice detail page if the invoice is paid
     * from the "My Purchased Apps" page

7. Public download URL

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Lướt qua các tính năng
======================

1. Tạo và quản lý Odoo module với nhiều phiên bản so với các phiên bản Odoo
2. Tích hợp với sản phẩm của Odoo
3. Tích hợp với hóa đơn để quản lý thanh toán dựa trên doanh thu module của bạn
4. Tich hợp với ứng dụng quản lý Git cho phép

   * Thêm các nhánh git có chứa ứng dụng/modules odoo của bạn
   * Quét các nhánh và tự động phát hiện ứng dụng/modules odoo của bạn
   * Lên lịch tự động quét các nhánh theo chu kỳ

5. Đồng bộ hóa dữ liệu module với Sản phẩm

   * Tự động tạo sản phẩm mới hoặc kết nối với các sản phẩn đã có được xác định bởi mã sản phẩm và tên mã module
   * Nối phiên bản Odoo với thuộc tính sản phẩm
   * Tự động cập nhật ảnh, giá, giá nhà cung cấp, bản quyền của sản phẩm (Nhờ được kết nối với ứng dụng quản lý bản quyền sản phẩm), ...

6. Cổng ứng dụng khách hàng tải xuống

   * Khách hàng có thể đăng nhập vào cổng thông tin của bạn và tải về ứng dụng họ đã mua trước đó

     * từ trang thông tin hóa đơn nếu hóa đơn đã được thanh toán
     * từ trang "Ứng dụng đã mua của tôi"

7. URL tải về công khai

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com/apps/app/14.0/to_odoo_module",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Odoo Apps',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['to_token_expiration', 'account', 'to_product_odoo_version', 'to_git_odoo_version', 'to_product_license'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'data/partner_data.xml',
        'data/product_category_data.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/odoo_module_version_image_views.xml',
        'views/odoo_module_version_views.xml',
        'views/odoo_module_views.xml',
        'views/product_template_views.xml',
        'views/git_branch_views.xml',
        'views/git_repository_views.xml',
        'views/software_author_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/odoo_module_version_download_stat_views.xml',
        'views/apps_portal_templates.xml',
        'report/account_invoice_report_view.xml',
        'wizard/wizard_git_url_add_views.xml',
        'wizard/wizard_odoo_module_version_download_views.xml',
        'wizard/wizard_odoo_module_version_public_download_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 495.9,
    'subscription_price': 27.31,
    'currency': 'EUR',
    'license': 'OPL-1',
}
