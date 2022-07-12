# -*- coding: utf-8 -*-
{
    'name': "Sales Teams Advanced",
    'name_vi_VN': "Nhóm bán hàng nâng cao",
    'summary': """
Adding more sales access groups""",
    'summary_vi_VN': """
Thêm nhiều nhóm truy cập bán hàng""",
    'description': """
What it does
============
This module provides suitable sales access rights for businesses, this will helps secure sales information by teams, regions and assign access rights to the suitable users.

Key Features
============
Businesses with a large sales team will need to divide the sales team into teams, regions. So, this module rearranges Access Groups and Security Policies in the Sales app as follows:

#. Access Groups

   * **Sales / User: Own Documents Only**: This is the default group in Odoo.
   * **Sales / Sales Team Leader**: The new access group that inherits **Sales / User: Own Documents Only**
   * **Sales / Regional Manager**: The new access group that inherits the group **Sales / Sales Team Leader**
   * **Sales / User: All Documents**: This is the default group in Odoo. It now inherits **Sales / Regional Manager** instead of **Sales / User: Own Documents Only**
   * **Sales / Administrator**: Full access to Sales Management application

#. Security Policies

   * **Sales / User: Own Documents Only**: Only view information in their own sales application
   * **Sales / Sales Team Leader**: View/edit team of which she or he is either a member or the team leader 
   * **Sales / Regional Manager**: View/edit/create/delete team of which she or he is either a member or the team leader or the regional manager 
   * **Sales / User: All Documents**: Full access for all teams except the sales configuration
   * **Sales / Administrator**: Full access to Sales Management application, including the configuration

Notes
-----

When installing this module, it will not set up advanced sales team settings. Therefore, depending on the situation, you can install this module with the extra modules that you need, the details as follows:

* If you have the CRM application, you may need to install the module CRM - Sales Teams Advanced (to_sales_team_advanced_crm): https://viindoo.com/apps/app/13.0/to_sales_team_advanced_crm
* If you have the Sales Manager (sale_management), you  may need to install the module Sales - Sales Teams Advanced (to_sales_team_advanced_sale): https://viindoo.com/apps/app/13.0/to_sales_team_advanced_sale

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này cung cấp tính năng phân cấp bán hàng phù hợp hơn cho doanh nghiệp, việc phân cấp này sẽ giúp bảo mật thông tin bán hàng theo từng đội nhóm, khu vực và phân quyền truy cập cho người dùng phù hợp.

Tính năng nổi bật
=================
Các doanh nghiệp có đội bán hàng đông đảo sẽ có nhu cầu chia đội bán hàng thành các đội, theo khu vực. Vì vậy, mô-đun này sắp xếp lại các nhóm phân quyền trong ứng dụng Bán hàng như sau:

#. Nhóm truy cập

   * **Bán hàng / Người dùng: Chỉ tài liệu của chính mình**: Đây là nhóm mặc định trong Odoo.
   * **Bán hàng / Trưởng đội bán hàng**: Nhóm truy cập mới kế thừa nhóm **Bán hàng / Người dùng: Chỉ tài liệu của chính mình**
   * **Bán hàng / Giám đốc khu vực**: Nhóm truy cập mới kế thừa nhóm **Bán hàng / Đội trưởng bán hàng**
   * **Bán hàng / Người dùng: Tất cả tài liệu**: Đây là nhóm mặc định trong Odoo. Bây giờ nó kế thừa **Bán hàng / Người quản lý khu vực** thay vì **Bán hàng / Người dùng: Chỉ tài liệu của chính mình**
   * **Bán hàng / Quản trị viên**: Đầy đủ quyền truy cập đến ứng dụng Quản lý bán hàng.

#. Chính sách bảo mật

   * **Bán hàng / Người dùng: Chỉ tài liệu của chính mình**: Chỉ xem được các thông tin ở ứng dụng bán hàng của mình
   * **Bán hàng / Trưởng đội bán hàng**: Xem/chỉnh sửa các thông tin về phần bán hàng trong nhóm/khu vực mà mình quản lý 
   * **Bán hàng / Giám đốc khu vực**: Xem/sửa/tạo/xóa các thông tin về phần bán hàng trong nhóm/khu vực mà mình quản lý
   * **Bán hàng / Người dùng: Tất cả tài liệu**: Đầy đủ quyền, trừ phần cấu hình trong ứng dụng Bán hàng
   * **Bán hàng / Quản trị viên**: Đầy đủ quyền, bao gồm cả phần cấu hình trong ứng dụng Bán hàng

Ghi chú
-------
Mô-đun này khi được cài đặt lên sẽ chưa tạo các thiết lập đội nhóm bán hàng nâng cao. Vì vậy, tùy vào tình huống sử dụng, bạn có thể cài đặt mô-đun này kèm với mô-đun mà bạn cần sử dụng thêm, chi tiết như sau: 

* Khi bạn đã cài đặt ứng dụng CRM, bạn có thể sẽ cần cài thêm mô-đun CRM - Nhóm bán hàng nâng cao (to_sales_team_advanced_crm): https://viindoo.com/apps/app/13.0/to_sales_team_advanced_crm
* Khi bạn đã cài đặt Quản lý bán hàng (sale_management), bạn có thể sẽ cần cài thêm mô-đun Bán hàng - Nhóm bán hàng nâng cao (to_sales_team_advanced_sale): https://viindoo.com/apps/app/13.0/to_sales_team_advanced_sale

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'images':['images/main_screenshot.png'],
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sales_team'],

    # always loaded
    'data': [
        'security/sales_team_security.xml',
        'security/ir.model.access.csv',
        'views/crm_team_region_views.xml',
        'views/crm_team_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
