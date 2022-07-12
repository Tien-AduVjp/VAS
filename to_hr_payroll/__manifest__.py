{
    'name': 'Payroll',
    'name_vi_VN': 'Bảng lương',
    'category': 'Human Resources/Payroll',
    'version': '1.4.7',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': "https://viindoo.com/intro/payroll",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': 'Manage your employee payroll records',
    'summary_vi_VN': 'Quản lý hồ sơ lương nhân viên của bạn',
    'description': """

Problems
========

* Payroll work in enterprises often takes a lot of time due to:

  * Large number of employees.
  * Apply many different salary modes, different calculation formulas for different positions.
  * To synthesize data for monthly salary calculation, enterprises need to spend a lot of personnel to monitor and analyse data from departments and workshops, etc.
  * Enterprises work in flexible shifts: the working form of each employee is different IN the number of breaks, the number of overtime shifts, commissions, discounts, etc. making salary calculation complicated, confusing the payroll department.

* The enduring time to analyze and calculate salary leads to the consequence of updating the general data of the enterprise, affecting the financial, production and business planning.
* It's difficult to analyze the detail of costs related to salary by department, by project or by some other purpose.
* The accuracy of the data depends a lot on the carefulness and presentation skills of the payroll personnel.
* To build salary cost analysis reports for each department, each purpose in a long period of time is quite time consuming, and it is not easy to get updated data right when the need arises.

This module takes data from several modules such as Attendances (hr_attendance), Time Off (hr_holidays), Employees (hr), HR Payroll Accounting (to_hr_payroll_account), etc. to calculate salary scientifically and transparently.

Key Features
============
This module allows:

#. Create Payslip and Payslips Batches

   * With just a few clicks, users can create individual Payslip for each employee, Payslips Batches for all employees in the company. The information about the contract, salary structure, working time, vacation time, insurance contributions, income tax.etc. are automatically updated on the payslip to serve as a basis for salary calculation.
   * Attach a Payslip to an existing Payslips Batches.
   * Send Payslips Batches to the bank if the enterprise chooses to transfer employee's salary via bank account.

#. Integrated Payroll applications:

   * Contracts: The system will base on the information on the contract to calculate salary such as applicable employee salary structure, contract start date, salary, etc.
   * Employees: Users can retrieve information for the payroll such as Company's Employee List, Attendances, Timesheets, etc.
   * HR Meal application: Just BY creating the employee's meals for the month in the HR Meal Application, the system will automatically subtract fees for the meals from that employee's most recent payroll.
   * Time Off application: The system will base on the information on the employee's leave slip to calculate the number of leave hours and calculate the salary.

#. Setup:

   * Salary rules with 2 options:

     * Choose a Payroll Localization: The system will redirect the users to the Application module to install the Vietnam Localized Payroll Applications.
     * Generate Payroll Rules: The system will automatically add system default salary rules (In case 1 or more default salary rules have been deleted). These salary rules can be grouped into a group like Allowance group, Deduction group, etc.

   * Salary structure: Allows creating different salary structures such as salary structure for office block, salary structure for production block, etc.
   * Personal tax rules according to Vietnam's regulations.
   * Payroll Contribution Register / Payroll Contribution Type: Helps to classify contributions by groups involved in the process of making wages such as Employees, insurance agencies, unions, etc.
   * HR Advantage Templates: Allows setting up employee's advantage as specified in the labor contract and according to the company's regulations such as toxic/job-specific allowance, diligence bonus, Performance bonus.vv

#. Record a payslip and Payslips Batches:

   * Record a payslip: Automatically create payroll entries for accountants if ```Payroll Entries``` is enabled in ```Setup```>```Payroll```.
   * Record a payroll for employee's salary security needs: When activating ```Payslip Batch Journal Entry``` in ```Setup```>```Payroll```, a single journal entry will be generated for all payslips belonging to the same payroll. Otherwise, each payslip will generate a journal entry.

#. Provide reports with visualized, multi-dimensional information:

   * Salary Analysis Report: Allows viewing the criteria included in the payroll which is designed in a Pivot table, allowing users to filter, group, or set up the Report table with the criteria that the user wants. monitor.
   * Payroll Contribution History: Users can look up and manage the contributions of a specific employee with the following criteria:

     * Basis of calculation
     * Start day
     * End date
     * Status
     * etc.

   * Analyse Payslip Personal Income Tax Analysis in many dimensions with calculated values such as:

     * Tax value
     * Tax base
     * Taxable income
     * etc.

Known Issues
============
#. With the salary cycle, has a limited about the day negative day. You can replace it by setting the positive day and negative month.
#. In case the payslip includes multiple contracts:

    * Salary Rules will be calculated based on the salary structure of the latest contract.
    * Payslip lines related to advantages will be calculated based on advantages of the latest contract.

Editions Supported
==================
1. Community Edition

    """,
    'description_vi_VN': """
Mô đun Bảng lương giải quyết một số bài toán của doanh nghiệp
=============================================================
* Công tác tiền lương trong doanh nghiệp thường tốn rất nhiều thời gian do:

  * Số lượng nhân viên lớn.
  * Áp dụng nhiều chế độ tiền lương khác nhau, công thức tính toán khác nhau cho các đối tượng khác nhau.
  * Để tổng hợp số liệu phục vụ cho công tác tính toán tiền lương hàng tháng, doanh nghiệp cần tốn khá nhiều nhân sự để theo dõi, tổng hợp số liệu từ các phòng ban, phân xưởng, v.v.
  * Doanh nghiệp làm việc ca kíp linh động, hình thức làm việc của mỗi nhân viên khác nhau: số buổi nghỉ, số ca làm thêm giờ, hoa hồng, chiết khấu, v.v. làm cho việc tính tiền lương trở nên phức tạp, dễ gây nhầm lẫn cho bộ phận quản lý lương.

* Thời gian tổng hợp và tính toán lương kéo dài dẫn đến hệ lụy về việc cập nhật số liệu chung của doanh nghiệp, ảnh hưởng đến việc hoạch định kế hoạch tài chính, sản xuất, kinh doanh.
* Việc phân tích chi phí liên quan đến tiền lương khó để chi tiết theo từng bộ phận, từng dự án hoặc theo một số mục đích khác.
* Độ chính xác của dữ liệu phụ thuộc khá nhiều vào sự cẩn trọng và kỹ năng trình bày của nhân sự làm lương.
* Để xây dựng các báo cáo phân tích chi phí lương cho từng bộ phận, từng mục đích với một khoảng thời gian dài khá tốn thời gian và để có được số liệu cập nhật ngay khi có nhu cầu không hề dễ dàng.

Mô đun này lấy dữ liệu từ một số module như Quản lý Vào/Ra (hr_attendance), Quản lý Ngày nghỉ (hr_holidays), Quản lý Nhân viên, Kế toán lương (to_hr_payroll_account), v.v. để tính lương một cách khoa học và minh bạch.

Tính năng cơ bản
================
Mô đun này cho phép:

#. Tạo Phiếu lương và tạo Bảng lương nhanh chóng

   * Chỉ với một vài nhấp chuột, người dùng có thể tạo Phiếu lương riêng lẻ cho từng nhân viên, Bảng lương cho toàn bộ nhân viên trong công ty. Các thông tin về hợp đồng, cấu trúc lương, thời gian làm việc, thời gian nghỉ, các khoản đóng góp về bảo hiểm, thuế thu nhập, v.v. đều được tự động cập nhật vào phiếu lương để làm căn cứ tính lương.
   * Gắn một Phiếu lương đến một Bảng lương có sẵn.
   * Gửi Bảng lương cho ngân hàng nếu doanh nghiệp chọn hình thức chuyển tiền lương của nhân viên qua tài khoản ngân hàng.

#. Các ứng dụng tích hợp tính lương:

   * Hợp đồng lao động: Hệ thống sẽ dựa vào các thông tin trên hợp đồng để làm cơ sở tính lương như Cấu trúc lương nhân viên áp dụng, Ngày bắt đầu hợp đồng, Tiền công/Tiền lương, v.v.
   * Hồ sơ nhân viên: Có thể truy xuất các thông tin để phục vụ cho bảng lương như Danh sách nhân viên của công ty, Dữ liệu Vào/Ra, Bảng chấm công, v.v.
   * Ứng dụng quản lý suất ăn: Chỉ cần tạo ra các suất ăn của nhân viên trong tháng ở Ứng dụng Suất ăn, hệ thống sẽ tự động trừ vào bảng lương gần nhất của nhân viên đó.
   * Ứng dụng quản lý nghỉ: Hệ thống sẽ dựa vào thông tin trên phiếu nghỉ của nhân viên và tính toán ra số giờ nghỉ và tính toán lương.

#. Thiết lập:

   * Quy tắc lương với 2 lựa chọn:

     * Chọn quy tắc Tiền lương bản địa: Hệ thống sẽ chuyển hướng người dùng đến mô đun Ứng dụng để cài đặt các Ứng dụng Tính lương Bản địa hóa của Việt Nam.
     * Tạo các quy tắc lương: Hệ thống sẽ tự động bổ sung thêm các quy tắc lương mặc định của hệ thống (Trong trường hợp 1 hay nhiều quy tắc lương mặc định đã bị xóa). Các quy tắc lương này có thể được nhóm lại thành một nhóm như nhóm Phụ cấp, nhóm Giảm trừ, v.v.

   * Cấu trúc lương: Cho phép tạo ra nhiều cấu trúc lương khác nhau như là cấu trúc lương cho khối văn phòng, cấu trúc lương cho khối sản xuất hoặc theo vị trí công việc, v.v. Có thể gán một cấu trúc lương với một vị trí công việc giúp cho việc nhập dữ liệu đối với một nhân viên mới thuận tiện và nhanh chóng hơn.
   * Quy tắc Thuế TNCN theo quy định của Việt Nam.
   * Ghi nhận Đóng góp/Nhóm Ghi nhận Đóng góp: Giúp phân loại các khoản đóng góp bởi các nhóm đối tượng tham gia vào quá trình cấu thành nên tiền lương như Người lao động, cơ quan bảo hiểm, công đoàn, v.v.
   * Mẫu Chế độ Đãi ngộ cho Hợp đồng: Cho phép thiết lập các khoản đãi ngộ của người lao động được quy định trên hợp đồng lao động và theo quy chế công ty như Trợ cấp độc hại/đặc thù nghề, Thưởng chuyên cần, Thưởng hiệu quả công việc, v.v.

#. Định khoản một phiếu lương và Định khoản cả bảng lương:

   * Định khoản một phiếu lương: Tự động tạo các bút toán lương cho kế toán nếu kích hoạt ```Kế toán lương``` trong mục ```Thiết lập```>```Bảng lương```.
   * Định khoản cả bảng lương phục vụ nhu cầu bảo mật lương cho người lao động: Khi kích hoạt ```Bút toán cho Bảng lương``` trong mục ```Thiết lập```>```Bảng lương```, một bút toán duy nhất sẽ được sinh ra cho tất cả các phiếu lương thuộc cùng một bảng lương. Ngược lại, mỗi phiếu lương sẽ có riêng một bút toán kế toán.

#. Cung cấp các báo cáo với thông tin trực quan, đa chiều:

   * Báo cáo Phân tích Lương: Cho phép xem các chỉ tiêu có trong bảng lương và được thiết kế với giao diện Pivot, giúp người dùng có thể lọc, nhóm, hay tự mình thiết lập bảng Báo cáo với chỉ tiêu mà người dùng muốn theo dõi.
   * Lịch sử đóng góp từ lương: Người dùng có thể tra cứu, quản lý những khoản một nhân viên cụ thể đóng góp với các tiêu chí:

     * Cơ sở tính toán
     * Ngày bắt đầu
     * Ngày kết thúc
     * Tình trạng
     * v.v.

   * Phân tích Thuế thu nhập cá nhân theo nhiều chiều với các giá trị tính toán như:

     * Giá trị thuế
     * Cơ sở tính thuế
     * Thu nhập bị tính thuế
     * v.v.

Vấn đề hiện tại
===============
#. Với chu kỳ lương, có một hạn chế về ngày âm. Bạn có thể thay thế nó bằng cách thiết lập ngày dương và tháng âm.
#. Trong trường hợp phiếu lương có nhiều hợp đồng:

    * Quy tắc lương sẽ được tính toán dựa trên cấu trúc lương của hợp đồng mới nhất.
    * Dòng phiếu lương liên quan đến các khoản phụ cấp sẽ được tính toán dựa trên các khoản phụ cấp của hợp đồng mới nhất.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community

    """,
    'depends': [
        'to_base',
        'viin_hr',
        'hr_org_chart',
        'to_hr_contract_actions',
        'to_hr_employee_relative',
        'viin_hr_holidays',
        'viin_hr_employee_resource_calendar',
    ],
    'data': [
        'views/assets.xml',
        'views/hr_payroll_report.xml',
        'data/mail_template_data.xml',
        'data/hr_contribution_category_data.xml',
        'data/hr_payroll_data.xml',
        'data/scheduler_data.xml',
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_contract_views.xml',  # this contains some root menus
        'views/hr_salary_cycle_views.xml',
        'views/hr_advantage_template_views.xml',
        'views/hr_department_views.xml',
        'views/hr_job_view.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_payroll_structure_views.xml',
        'views/hr_salary_rule_category_views.xml',
        'views/hr_contribution_category.xml',
        'views/hr_contribution_register_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_line_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_working_month_calendar_line_views.xml',
        'views/hr_working_month_calendar_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_holidays_summary_employee_views.xml',
        'wizard/abstract_hr_payroll_contrib_action_view.xml',
        'wizard/hr_payroll_contrib_action_change_base_view.xml',
        'wizard/hr_payroll_contrib_action_change_rates_view.xml',
        'wizard/hr_payroll_contrib_action_done_view.xml',
        'wizard/hr_payroll_contrib_action_resume_view.xml',
        'wizard/hr_payroll_contrib_action_edit_date_start_views.xml',
        'wizard/hr_payroll_contrib_action_edit_date_end_views.xml',
        'wizard/hr_payroll_contrib_action_suspend_view.xml',
        'wizard/update_contract_advantage_views.xml',
        'views/hr_payroll_contribution_register.xml',
        'views/hr_payroll_contribution_type.xml',
        'views/hr_payroll_contribution_history.xml',
        'views/hr_payroll_analysis.xml',
        'views/personal_tax_rule_views.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contributionregister_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslipdetails_templates.xml',
        'views/report_payslipbatch_templates.xml',
        'views/hr_payroll_contribution_analysis.xml',
        'views/hr_employee_relative_views.xml',
        'report/payslip_personal_income_tax_analysis.xml',
    ],
    'demo': [
        'data/user_demo.xml',
        'data/personal_tax_rule_demo.xml',
        'data/hr_contract_demo.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 198.9,
    'subscription_price': 12.6,
    'currency': 'EUR',
    'license': 'OPL-1',
}
