{
    'name': "CRM - Sales Teams Advanced",
    'name_vi_VN': "CRM - Đội bán hàng nâng cao",
    'summary': """
Integrate Sales Team Advanced with CRM""",
    'summary_vi_VN': """
Tích hợp đội bán hàng nâng cao với CRM""",
    'description': """
What it does
============
This module extends the CRM application with multiple sales teams that set up by the Sales Teams Advanced" module (to_sales_team_advanced), which helps companies can build and manage sales teams according to their needs.

Key Features
============
* Improve access rights to CRM module
* Add filtering and grouping by regions, sales team on reports in the CRM module
* Provides suitable sales access rights for businesses, this will helps secure sales information by teams, regions.

Businesses with a large sales team will need to divide the sales team into teams, regions. So, this module rearranges Access Groups and
Security Policies in the Sales application as follows:

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

Note
----

For Sales & CRM Integration, you may also want to check out the module Sales - Sales Teams Advanced: https://viindoo.com/apps/app/13.0/to_sales_team_advanced_sale

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này mở rộng ứng dụng CRM với nhiều đội bán hàng được thiết lập bởi mô-đun Nhóm bán hàng nâng cao (to_sales_team_advanced), giúp các doanh nghiệp cho thể xây dựng, phân chia quản lý các đội bán hàng theo nhu cầu.

Tính năng nổi bật
=================
* Cải thiện quyền truy cập vào mô-đun CRM
* Thêm các bộ lọc nhóm theo khu vực, đội nhóm bán hàng trên các báo cáo ở mô-đun CRM
* Cung cấp tính năng phân cấp bán hàng phù hợp hơn cho doanh nghiệp, việc phân cấp này sẽ giúp bảo mật thông tin bán hàng theo từng đội nhóm, khu vực.

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

Ghi chú
-------

Để tích hợp Bán hàng và CRM, bạn cũng có thể tham khảo mô-đun Bán hàng - Đội bán hàng nâng cao (to_sales_team_advanced_sale): https://viindoo.com/apps/app/13.0/to_sales_team_advanced_sale

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_sales_team_advanced', 'crm'],

    # always loaded
    'data': [
        'security/crm_security.xml',
        'report/crm_activity_report_views.xml',
        'report/crm_opportunity_report_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_team_region_views.xml',
        'views/root_menu.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'uninstall_hook': 'uninstall_hook',
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
