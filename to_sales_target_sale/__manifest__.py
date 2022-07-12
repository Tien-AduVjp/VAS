{
    'name': "Sales Target Management - Sales Management",
    'name_vi_VN': "Quản lý mục tiêu doanh số - Quản lý bán hàng",
    'summary': """
Integrated Sales Target Management with Sales Application""",
    'summary_vi_VN': """
Tích hợp ứng dụng quản lý mục tiêu doanh số với ứng dụng bán hàng""",
    'description': """
What it does
============
This module integrates the Sales Target Management application and the Sales Management to allow you to manage sales targets for sales persons and sales team in the Sales Management application

Key Features
============
1. Sales Targets for salespersons in Sales Management application

    * Salespersons submit their target
    * Sales Team Leader approves/refuses/adjusts the target

2. Manage Sales Targets for Sales Teams in Sales Management application

    * Team Leader register their team's sales target
    * Regional Sales Manager can either approve or refuse and request changes

3. Measure sales targets in reach automatically

    * With Individuals / Salespersons

        * For Sales

            * Sales Total for the period of the sales target
            * Target Reached (in percentage (%), based on the sales of sales orders)

        * For Invoiced

            * Invoiced Total during the target period
            * Target Reached (in percentage (%), based on the invoiced value)

    * With A Sales Team

        * For Sales

            * Sales Total for the period of the sales target
            * Target Reached (in percentage (%), based on the sales of sales orders)

        * For Invoiced

            * Invoiced Total during the target period
            * Target Reached (in percentage (%), based on the invoiced value)

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này tích hợp ứng dụng Quản lý mục tiêu doanh số và Quản lý bán hàng để cho phép bạn quản lý mục tiêu doanh số cho nhân viên kinh doanh và đội bán hàng trong ứng dụng Quản lý bán hàng

Tính năng nổi bật
=================
1. Quản lý mục tiêu doanh số cho nhân viên bán hàng trong ứng dụng Quản lý bán hàng

    * Nhân viên bán hàng đề xuất mục tiêu doanh số của họ
    * Đội trưởng bán hàng có quyền phê duyệt/điều chỉnh/từ chối mục tiêu doanh số do nhân viên đề xuất

2. Quản lý mục tiêu doanh số cho các đội bán hàng trong ứng dụng Quản lý bán hàng

    * Đội trưởng đăng ký mục tiêu doanh số của đội mình
    * Quản lý bán hàng khu vực có quyền phê duyệt/điều chỉnh/từ chối mục tiêu doanh số

3. Đo lường mục tiêu bán hàng tự động

    * Dành cho cá nhân/nhân viên kinh doanh

        * Đối với Bán hàng

            * Tổng doanh số được xác nhận trong thời gian của mục tiêu doanh số
            * Mục tiêu đã đạt (tính theo phần trăm (%), tính trên doanh số của đơn bán)

        * Dựa trên Hóa đơn đã xuất

            * Tổng doanh số đã được xuất hóa đơn trong thời gian của mục tiêu
            * Mục tiêu đã đạt (tính theo phần trăm (%), tính trên giá trị đã xuất hóa đơn)

    * Dành cho đội bán hàng

        * Đối với Bán hàng

            * Tổng doanh số được xác nhận trong thời gian của mục tiêu doanh số
            * Mục tiêu đã đạt (tính theo phần trăm (%), tính trên doanh số của đơn bán)

        * Dựa trên Hóa đơn đã xuất

            * Tổng doanh số đã được xuất hóa đơn trong thời gian của mục tiêu
            * Mục tiêu đã đạt (tính theo phần trăm (%), tính trên giá trị đã xuất hóa đơn)

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
    'depends': ['sale_crm', 'to_sales_target', 'to_sales_team_advanced_sale'],

    # always loaded
    'data': [
        'data/scheduler_data.xml',
        'views/crm_team_views.xml',
        'views/personal_sales_target_views.xml',
        'views/team_sales_target_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
