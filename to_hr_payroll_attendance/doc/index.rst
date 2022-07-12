Installation
============

1. Navigate to Apps
2. Find with keyword 'to_hr_payroll_attendance'
3. Install it as usual then you are done

How to access attendance data from salary rules
===============================================

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

