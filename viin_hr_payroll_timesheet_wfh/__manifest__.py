# -*- coding: utf-8 -*-
{
    'name': "Payroll - Work From Home Timesheet",
    'name_vi_VN': "Bảng lương - Chấm công Làm việc tại nhà",

    'summary': """
Manage and calculate Time Off's working time with timesheet for the time off that is considered as working time (e.g. Work From Home)""",

    'summary_vi_VN': """
Quản lý chấm công giờ làm việc dùng bảng chấm công cho các kiểu nghỉ mà được coi là vẫn đi làm (vd: Làm việc tại nhà)
	""",

    'description': """
What it does
============

#. This module enables HR Managers to require all the time-off registers of a time-off type to have timesheet recorded
   for PoW (proof of work). Each individual employee also have an option to disable this requirement. For example,
   implement Work From Home for everyone in the company but the CEO:

   * Create a new time-off named "Work From Home" with `Is Unpaid` option unchecked
     and `PoW Timesheet Required` option checked).
   * Go to the employee profile of the CEO and uncheck the option 'PoW Timesheet Required'

#. Integrated with Payroll App (Viindoo Payroll App, not the Odoo EE Payroll) for calculation of the following in payslip:

   * PoW Timesheet Required Hours / Days
   * PoW Timesheet Recorded Hours / Days
   * Missing PoW Timesheet Hours / Days

#. The following salary rule will be generated for the BASE salary structures of existing company upon installation of
   this module so that the employee pay will be deducted with the amount base on: Missing PoW Hours * Timesheet Cost Per Hour

   .. code-block:: python

     result = -1 * payslip.missing_pow_hours * employee.timesheet_cost

   It is also generated for new company upon the company is created in the system

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Module này làm gì
=================

#. Module này cho phép người quản lý nhân sự có thể thiết lập một kiểu nghỉ nào đó mà khi nhân viên nghỉ theo kiểu đó thì
   bắt buộc phải ghi nhận PoW (Proof of Work, minh chứng có làm việc) thông qua việc chấm công ở ứng dụng Chấm công
   (Timesheet). Người quản lý nhân sự cũng có thể vô hiệu yêu cầu này đối với 1 vài nhân viên đặc biệt nào đó. Ví dụ:
   Triển khai làm việc tại nhà cho toàn công ty, yêu cầu mọi người đều phải chấm công để ghi nhận PoW, ngoại trừ CEO:

   * Tạo một kiểu nghỉ mới đặt tên là "Làm việc tại nhà" với tùy chọn `Không trả lương` không đánh dấu (tức là có trả lương)
     và tùy chọn `Yêu cầu chấm công PoW` được đánh dấu.
   * Đi đến hồ sơ nhân viên của CEO và chọn dấu chọn ở tùy chọn 'Yêu cầu chấm công PoW'

#. Tích hợp với ứng dụng Bảng lương (ứng dụng Bảng lương của Viindoo, không phải của Odoo EE) để phục vụ việc tính toán
   tự động các thông tin sau trên các phiếu lương:

   * Số Ngày / Giờ chấm công PoW bắt buộc
   * Số Ngày / Giờ chấm công PoW thực tế
   * Số Ngày / Giờ chấm công PoW còn thiếu

#. Quy tắc lương sau đâu sẽ được sinh ra cho tất cả các cấu trúc lương CƠ SỞ cho tất cả các công ty đang có trong hệ
   thống khi cài đặt module này để tính toán số tiền bị trừ theo công thức: `Số giờ không chấm công PoW * Chi phí mỗi giờ công`

   .. code-block:: python

     result = -1 * payslip.missing_pow_hours * employee.timesheet_cost

   Quy tắc này cũng được tự động sinh ra cho công ty mới khi một công ty mới được tạo trong hệ thống

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '0.1.2',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_timesheet_payroll', 'project_timesheet_holidays', 'viin_project_timesheet_leave'],

    # always loaded
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_leave_views.xml',
        'views/hr_timesheet_views.xml',
        'views/project_task_views.xml',
        'views/hr_working_month_calendar_line_views.xml',
        'views/hr_working_month_calendar_views.xml',
        'views/hr_payslip_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'images' : [
    	 'static/description/main_screenshot.png'
    	],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}