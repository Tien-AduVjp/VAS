# -*- coding: utf-8 -*-
{
    'name': "Payroll Attendance",
    'name_vi_VN': "Quản lý Vào/Ra - Tính lương",

    'summary': """Attendance and Payroll Integration""",
    'summary_vi_VN': """Tích hợp Quản lý Vào/Ra và Tính lương
    	""",

    'description': """
What it does
============
This module connects the Attendance and Payroll modules, allowing users to automatically load all employees' attendance data into payslips, as a base for payroll.

Key Features
============

After installing this module, in addition to the Working Calendar Info, Leave Summary, a Summary of Attendance will be added on the employee's
pay slip with the following information:

   * Late Coming Hours: total hours of late coming during the payslip period.
   * Early Leave Hours: total hours of early leaves during the payslip period.
   * Late Comings: number of times the employee came late during the payslip period.
   * Early Leaves: number of times the employee leave earlier that the expected contracted check-out time during the payslip period.
   * Missing Check-outs: the number of times the employee forgot to check-out during the payslip period.
   * Total Attendance (in hours): The total time that the employee had been attending during the payslip period.
   * Total Valid Attendance (in hours): The total valid time (that matches the employee's contracted working schedule) that the employee had been attending during the payslip period.

All these data is automatically loaded from the Attendance module.

How to access attendance data from salary rules
-----------------------------------------------

.. code-block:: python

  # to get the employee attendance entries during the payslip period
  attendance_entries = payslip.attendance_ids
  # to get total attendance hours
  total_attendance_hours = payslip.total_attendance_hours
  # to get valid attendance hours
  valid_attendance_hours = payslip.valid_attendance_hours
  # to get total late coming hours
  late_attendance_hours = payslip.late_attendance_hours
  # to get total early leave hours
  early_leave_hours = payslip.early_leave_hours
  # to get number of late comes
  late_attendance_count = payslip.late_attendance_count
  # to get number of early leave
  early_leave_count = payslip.early_leave_count
  # to get number of times the employee forget to checkout
  missing_checkout_count = payslip.missing_checkout_count

**An example of basic wage computation based on total valid attendance**

.. code-block:: python

  result = 0.0
  # Loop over the payslip's working calendar lines that link to contract for wage calculation
  for line in working_month_calendar_lines.filtered(lambda l: l.contract_id):
      result += line.contract_id.wage * line.valid_attendance_hours / line.calendar_working_hours

**An example of missing checkout penalty**

Assume each missing checkout would cost $5

.. code-block:: python

  result = 5 * payslip.missing_checkout_count

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",

'description_vi_VN': """
Mô tả
=====
Quản lý Vào/Ra - Tính lương là mô đun nối giữa mô đun Quản lý Vào/Ra và Bảng lương, cho phép đẩy toàn bộ dữ liệu Quản lý Vào/Ra
của nhân viên vào phiếu lương một cách tự động, làm tiền đề cho việc tính toán lương.

Tính năng nổi bật
=================
Sau khi cài đặt mô đun này, ngoài Thông tin Lịch làm việc, Tổng hợp nghỉ, trên phiếu lương của nhân viên sẽ được bổ sung mục
Tóm tắt có mặt gồm các thông tin sau:

   * Số giờ đến muộn: Tổng số giờ đến muộn trong thời gian ghi phiếu lương
   * Số giờ về sớm: Tổng số giờ nghỉ sớm trong thời gian tính lương
   * Số lần đến muộn: Số lần nhân viên đến muộn trong kỳ phiếu lương
   * Số lần về sớm: Số lần nhân viên về sớm trong thời gian tính lương
   * Số lần quên đăng xuất: Số lần nhân viên quên đăng xuất trong kỳ phiếu lương
   * Tổng số giờ có mặt: Tổng thời gian nhân viên có mặt trong kỳ phiếu lương
   * Số giờ có mặt hợp lệ: Tổng thời gian hợp lệ (phù hợp với lịch làm việc theo hợp đồng của nhân viên) trong kỳ phiếu lương

Dữ liệu của các thông tin này sẽ được tự động trích xuất từ mô đun Quản lý Vào/Ra.

Cách truy cập dữ liệu chấm công từ các quy tắc lương
----------------------------------------------------

.. code-block:: python

  # to get the employee attendance entries during the payslip period
  attendance_entries = payslip.attendance_ids
  # to get total attendance hours
  total_attendance_hours = payslip.total_attendance_hours
  # to get valid attendance hours
  valid_attendance_hours = payslip.valid_attendance_hours
  # to get total late coming hours
  late_attendance_hours = payslip.late_attendance_hours
  # to get total early leave hours
  early_leave_hours = payslip.early_leave_hours
  # to get number of late comes
  late_attendance_count = payslip.late_attendance_count
  # to get number of early leave
  early_leave_count = payslip.early_leave_count
  # to get number of times the employee forget to checkout
  missing_checkout_count = payslip.missing_checkout_count

**Ví dụ về tính lương cơ bản dựa trên tổng số lần Vào/Ra hợp lệ**

.. code-block:: python

  result = 0.0
  # Loop over the payslip's working calendar lines that link to contract for wage calculation
  for line in working_month_calendar_lines.filtered(lambda l: l.contract_id):
      result += line.contract_id.wage * line.valid_attendance_hours / line.calendar_working_hours

**Ví dụ về hình thức phạt khi quên chấm Ra**

Mỗi lần quên chấm Ra sẽ bị mất $5.

.. code-block:: python

  result = 5 * payslip.missing_checkout_count


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_payroll', 'hr_attendance', 'viin_hr_attendance_validation'],

    # always loaded
    'data': [
        'views/hr_attendance_views.xml',
        'views/hr_working_month_calendar_line_views.xml',
        'views/hr_working_month_calendar_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/report_payslip_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': ['to_hr_payroll', 'hr_attendance'],
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
