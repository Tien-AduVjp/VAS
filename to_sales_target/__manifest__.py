# -*- coding: utf-8 -*-
{
    'name': "Sales Target",
    'name_vi_VN': "Mục tiêu Doanh số",

    'summary': """
Sales targets for individual sales persons and sales teams.
""",
    'summary_vi_VN': """
Mục tiêu doanh số cho nhân viên kinh doanh và đội bán hàng.
""",
    'description': """
What it does
============
* Manage Sales Targets for your salespersons and sales teams
* Ready to get extended in other applications

Key Features
============
#. Many sales teams are well organized thanks to the Sales Teams Advanced app (to_sales_team_advanced)

   * Sales / User: Own Documents Only
   * Sales / Sales Team Leader
   * Sales / Regional Manager
   * Sales / User: All Documents
   * Sales / Administrator

#. Submit and Approval Process

   * Individual Targets

     * Salespersons submit their target
     * Sales Team Leader approves/refuses/adjusts the target

   * Team Targets

     * Team Leader register their team's sales target
     * Regional Sales Manager can either approve or refuse and request changes

#. Allow to discuss and exchange of information on the Sales target application (to_sales_target) thanks to the Odoo's mail thread

   * Managers leave comments, request changes, etc
   * Submitters explain, ask for recommendation, etc

#. Ready for extending sales related applications:

   * Auto target reach measurement for Sales: https://viindoo.com/apps/app/13.0/to_sales_target_sale
   * Auto target reach measurement for Points of Sales: https://viindoo.com/apps/app/13.0/to_sales_target_pos

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Quản lý mục tiêu doanh số của nhân viên kinh doanh và đội bán hàng
* Sẵn sàng để mở rộng cho các ứng dụng khác

Tính năng nổi bật
=================
#. Nhiều nhóm bán hàng được tổ chức tốt nhờ vào ứng dụng Nhóm bán hàng nâng cao (to_sales_team_advanced)

   * Bán hàng / Người dùng: Chỉ tài liệu của chính mình
   * Bán hàng / Trưởng đội bán hàng
   * Bán hàng / Giám đốc khu vực
   * Bán hàng / Người dùng: Tất cả tài liệu
   * Bán hàng / Quản trị viên

#. Quản lý mục tiêu doanh số

   * Dành cho mục tiêu doanh số cá nhân

     * Nhân viên bán hàng đề xuất mục tiêu doanh số của họ
     * Đội trưởng bán hàng có quyền phê duyệt/điều chỉnh/từ chối mục tiêu doanh số do nhân viên đề xuất

   * Dành cho mục tiêu doanh số đội 

     * Đội trưởng đăng ký mục tiêu doanh số của đội mình
     * Quản lý bán hàng khu vực có quyền phê duyệt/điều chỉnh/từ chối mục tiêu doanh số

#. Cho phép thảo luận, trao đổi thông tin trên Mục tiêu doanh số (to_sales_target)

   * Người quản lý để lại nhận xét, yêu cầu thay đổi,...
   * Người gửi giải thích, đề xuất,...

#. Sẵn sàng cho việc mở rộng ứng dụng liên quan đến bán hàng:

   * Đo lường mục tiêu tự động cho doanh số Bán Hàng: https://viindoo.com/apps/app/13.0/to_sales_target_sale
   * Đo lường mục tiêu tự động cho Điểm bán hàng: https://viindoo.com/apps/app/13.0/to_sales_target_pos

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_sales_team_advanced'],

    # always loaded
    'data': [
        'security/sales_team_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/team_sales_target_views.xml',
        'views/personal_sales_target_views.xml',
        'views/crm_team_views.xml',
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
