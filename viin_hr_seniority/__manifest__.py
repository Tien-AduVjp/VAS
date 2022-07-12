# -*- coding: utf-8 -*-
{
    'name': "Employee Seniority",
    'name_vi_VN': "Thâm niên Nhân viên",

    'summary': """
Keep track of employee's service history in your company""",

    'summary_vi_VN': """
Theo dõi thâm niên công tác của nhân viên
    	""",

    'description': """
What it does
============
Basing on contract data, this module allows you to keep tracks of employee's service history
(e.g. boarding date, termination date, job position changes, department changes, service years, etc) in your company

Key Features
============
#. Employees will be able to see their own working history over the time
#. Managers will be able to see their subordinates working history over the time
#. HR Officers will be able to see all the employee seniority data
#. The views of pivot and list and graph allows you to analyze employee seniority in multiple dimensions
#. Employee Seniority Data is also available on employee records so that it can be accessible by other
   applications. For example, Payroll salary rule can take that data with:

   * `employee.employee_seniority_ids`: for the records of seniority crossing all the contracts
   * `employee.seniority_years`: for the years of service counting from the first contract's start date (incl. trial contracts)
   * `employee.seniority_months`: for the months of service counting from the first contract's start date (incl. trial contracts)
   * `employee.non_trial_seniority_years`: for the years of service counting from the first contract's start date (excl. trial contracts)
   * `employee.non_trial_seniority_months`: for the months of service counting from the first contract's start date (excl. trial contracts)
   * `employee.first_contract_date`: for the employee's boarding date, which is also the first contract's start date
   * `employee.first_non_trial_contract_date`: for the first non-trial contract's start date
   * `employee.termination_date`:the employee's off-boarding date, which is also the last contract's end date
   * etc

#. New employee filters: Hired last 30 days, Hire Last Year, Hire This Year, Terminated last 30 days,
   Terminated Last Year, Terminated This Year, etc

Demo Video: https://www.youtube.com/watch?v=0mdrw_PIx2A

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Module này làm gì
=================
Dựa trên dữ liệu hơp đồng, module này cho phép bạn theo dõi toàn bộ thâm niên công tác của nhân viên
(vd: ngày vào công ty, ngày rời công ty, thay đổi chức vụ, thay đổi phòng ban, số năm thâm niên, v.v.) trong công ty của bạn

Tính năng chính
===============
#. Nhân viên có thể xem lịch sử làm việc của chính mình qua thời gian
#. Người quản lý có thể xem lịch sử làm việc của cấp dưới của mình qua thời gian
#. Cán bộ Nhân sự xem và phân tích được toàn bộ dữ liệu thâm niên công tác của nhân viên toàn công ty
#. Các giao diện dang pivot, danh sách, đồ thị cho phép phân tích đa chiều
#. Dữ liệu thâm niên công tác cũng khả dụng ở hồ sơ nhân viên để các ứng dụng khác có thể truy cập. Ví dụ:
   quy tắc lương có thể lấy dữ liệu này bằng:

   * `employee.employee_seniority_ids`: để lấy dữ liệu các bản ghi thâm niên qua các hợp đồng
   * `employee.seniority_years`: để lấy số năm thâm niên (bao gồm cả thời gian hợp đồng thử việc)
   * `employee.seniority_months`: để lấy số tháng thâm niên (bao gồm cả thời gian hợp đồng thử việc)
   * `employee.non_trial_seniority_years`: để lấy số năm thâm niên (KHÔNG bao gồm thời gian hợp đồng thử việc)
   * `employee.non_trial_seniority_months`: để lấy số tháng thâm niên (KHÔNG bao gồm thời gian hợp đồng thử việc)
   * `employee.first_contract_date`: để lấy ngày vào công ty của nhân viên, cũng chính là ngày bắt đầu của hợp đồng đầu tiên
   * `employee.first_non_trial_contract_date`: để lấy ngày bắt đầu của hợp đồng chính thức đầu tiên
   * `employee.termination_date`: ngày nhân viên nghỉ việc, cũng chính là ngày kết thúc của hợp đồng cuối cùng
   * etc

#. Các bộ lọc nhân viên mới: Tuyển dụng trong 30 ngày qua, Tuyển dụng năm ngoái, Tuyển dụng năm nay,
   Nghỉ việc trong 30 ngày qua, Nghỉ việc năm ngoái, Nghỉ việc năm nay, v.v.

Video Demo: https://www.youtube.com/watch?v=0mdrw_PIx2A

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Employees',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'report/hr_employee_seniority_views.xml',
    ],

    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
