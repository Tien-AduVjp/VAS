# -*- coding: utf-8 -*-
{
    'name': "Time-Off Project Timesheet",
    'name_vi_VN': "Chấm công Nghỉ cho Dự án",

    'summary': """
Specify project and task on time-off""",

    'summary_vi_VN': """
Ấn định dự án và nhiệm vụ cho nghỉ
    	""",

    'description': """
What it does
============
Businesses have a need to manage employees who go on business trips or go out to perform some assigned tasks. At this time, managing the absence of employees at the office is required for businesses. So this module:

* Allows assigning a specific employee when the employee takes leave for business trips by linking the Time Off module (hr_holidays) to the Project module (project)
* Allows employees or managers to be able to set up projects and related employees with leave requests
* The cost of the time off of each employee can be calculated according to each specific employee and shown on the Project module based on that employee's time and hourly labor cost

Key Features
============
* Add a "Project Required" field on the Time Off Types. When asking for leave of absence from this Time Off Type, it is required to select a project to record Time off
* Add two "Related Project" and "Related Task" fields, allowing to select Projects and Tasks when applying for leave of absence
* Once the leave application is approved, a time sheet will be automatically generated on the selected task

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Doanh nghiệp có nhu cầu quản lý nhân viên đi công tác hoặc ra ngoài để thực hiện một số nhiệm vụ được giao.
Lúc này, doanh nghiệp có nhu cầu quản lý việc vắng mặt của nhân viên tại văn phòng. Vậy nên, mô-đun này:

* Cho phép gán một nhân viên cụ thể khi nhân viên xin nghỉ đi công tác bằng cách liên kết mô-đun Quản lý nghỉ (hr_holidays) và mô-đun Quản lý dự án (project)
* Cho phép nhân viên hoặc Quản lý có thể thiết lập dự án và nhân viên liên quan với các yêu cầu xin nghỉ
* Có thể thống kê chi phí cho thời gian nghỉ của từng nhân viên theo từng nhân viên cụ thể và được thể hiện trên mô-đun Quản lý dự án dựa vào thời gian và chi phí nhân công theo giờ của nhân viên đó

Tính năng nổi bật
=================
* Thêm trường "Project Required" trên Kiểu Nghỉ. Khi xin nghỉ trong Kiểu Nghỉ này, bắt buộc phải chọn 1 Dự án đi kèm để ghi nhận giờ vắng
* Bổ sung 2 trường "Related Project" và "Related Task", cho phép chọn Dự án và Nhiệm vụ khi xin nghỉ
* Khi xin nghỉ được duyệt thì tự động sinh ra bảng chấm công trên nhiệm vụ được chọn

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project_timesheet_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_analytic_line_views.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_leave_views.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
