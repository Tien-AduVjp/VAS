# -*- coding: utf-8 -*-
{
    'name': "Overtime",
    'name_vi_VN': "Tăng ca",

    'summary': """
Plan and Manage employees' overtime""",

    'summary_vi_VN': """
Lập kế hoạch và Quản lý tăng ca của cán bộ công nhân viên
    	""",

    'description': """
What it does
============
This application allows you to plan and manage your employee's overtime work

Key Features
============
1. Overtime Planning

   * HR User can register overtime plan for each and every employee in the company
   * Department Manager can register overtime plans for the team then get approved by top managers and HR.
   * This feature requires an additional module named *Overtime Approval* (by Viindoo, tech. name `viin_hr_overtime_approval`)

2. Overtime Recognition

   * By Plan: the register overtime plan will be considered as actual overtime. No other means required for overtime recognition
   * Attendance: the actual overtime work will be recognized by matching planned overtime registration with the actual attendance
     log. This feature requires an additional module *Overtime Attendance* (by Viindoo, tech. name `viin_hr_overtime_attendance`)
   * Timesheet: the actual overtime work will be recognized by matching planned overtime registration with the actual timesheet
     log. This feature requires an additional module *Overtime Timesheet* (by Viindoo, tech. name `viin_hr_overtime_timesheet`)

3. Overtime Costing

   * Defining overtime rules for any time interval of a day with Overtime Rate
   * Specify an Overtime Base Mode for employee contracts which is either

     * Manual Input: you can define any overtime base amount manually for the contract
     * Basic Wage: the overtime base amount will be the contract's basic wage
     * Gross Salary: the overtime base amount will be the contract's Gross Salary. This feature requires the module Viindoo HR Payroll (tech. name `to_hr_payroll`).
     * Wage Plus Configurable Advantages: the overtime base amount will be the contract's Wage plus the contract's advantages whose templates having Overtime Base Factor enabled. This feature requires the module Payroll (by Viindoo, tech. name `to_hr_payroll`).

   * Automatic matching overtime plan with the rule for automatic calculation of

     * Standard overtime cost: the overtime cost will be calculated as starndard contract rate multiple overtime hours
     * Overtime cost: the overtime cost will be calculated as starndard contract rate multiple overtime hours multiple pay rate

4. Multi-company supported

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Mô tả
=====
Ứng dụng này cho phép lập kế hoạch và quản lý tăng ca của cán bộ công nhân viên

Tính năng nổi bật
=================
1. Lập kế hoạch tăng ca

    * Nhân sự có thể đăng ký kế hoạch làm thêm giờ cho mỗi nhân viên trong công ty
    * Quản lý các phòng ban có thể đăng ký kế hoạch làm thêm giờ cho nhóm sau đó đề xuất phê duyệt bởi quản lý cấp cao và cán bộ nhân sự
    * Để sử dụng tính năng này, bạn cần cài đặt thêm mô-đun *Phê duyệt Tăng ca* (được phát triển bởi Viindoo, tên kỹ thuật là `viin_hr_overtime_approval`)

2. Ghi nhận Tăng ca

    * Theo kế hoạch: kế hoạch Tăng ca này có thể được coi như là Tăng ca thưc tế. Không cần công cụ nào khác để ghi nhận Tăng ca
    * Khớp với dữ liệu vào/ra: Thời gian tăng ca thực tế sẽ được ghi nhận bằng cách khớp các đăng ký tăng ca được lên kế hoạch sẵn với dữ liệu vào ra. Để sử dụng tính năng này, cần cài đặt bổ sung mô-đun *Điểm danh tăng ca* (được phát triển bởi Viindoo,tên kỹ thuật là `viin_hr_overtime_attendance`)
    * Chấm công: Thời gian tăng ca thực tế sẽ được ghi nhận bằng cách khớp các đăng ký tăng ca được lên kế hoạch sẵn vói dữ liệu chấm công. Để sử dụng tính năng này, cần cài đặt bổ sung mô-đun *Chấm công Tăng ca* (được phát triển bởi Viindoo,tên kỹ thuật là `viin_hr_overtime_timesheet`)

3. Chi phí Tăng ca

    * Định nghĩa quy tắc Tăng ca cho các khoảng thời gian trong ngày với tỷ lệ chi trả
    * Chỉ định cấu trúc tính lương tăng ca cơ bản trên hợp đồng lao động của nhân viên, có thể bao gồm:

        * Nhập thủ công: bạn có thể định nghĩa số tiền tăng ca cơ bản một cách thủ công trên hợp đồng
        * Lương cơ bản: lương tăng ca cơ bản sẽ là lương cơ bản trong hợp đồng
        * Tổng lương: tổng lương tăng ca sẽ là Tổng lương trên hợp đồng. Để sử dụng tính năng này, cần cài đặt Bảng lương (tên kỹ thuật là `to_hr_payroll`)
        * Lương cộng với phụ cấp có thể điều chỉnh: lương tăng ca cơ bản sẽ bằng lương trong hợp đồng cộng với trợ cấp trong hợp đồng đối với nhân viên có trường Số tiền cơ sở tính toán lương tăng ca. Để sử dụng tính năng này, cần cài đặt mô-đun "Bảng lương" (được phát triển bởi Viindoo, tên kỹ thuật là to_hr_payroll)

    * Tự động khớp kế hoạch tăng ca với quy tắc tính toán tự động của

      * Chi phí tăng ca tiêu chuẩn: chi phí tăng ca sẽ được tính toán bằng lương cơ bản trong hợp đồng nhân với số giờ tăng ca
      * Chi phí tăng ca: chi phí tăng ca sẽ được tính toán bằng lương cơ bản trong hợp đồng nhân với số giờ tăng ca nhân với tỷ lệ chi trả

4. Hỗ trợ sử dụng ở Môi trường Đa công ty

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/intro/overtime",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Overtime',
    'version': '0.1.5',

    # any module necessary for this one to work correctly
    'depends': ['to_base', 'hr_org_chart', 'viin_hr_employee_resource_calendar', 'to_hr_contract_actions'],

    # always loaded
    'data': [
        'data/cron_data.xml',
        # 'data/module_data.xml',
        'data/hr_overtime_reason.xml',
        'data/overtime_rule_code.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/abstract_overtime_plan_line_match_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'report/hr_employee_overtime_views.xml',
        'views/hr_overtime_plan_line_views.xml',
        'views/hr_overtime_plan_views.xml',
        'views/hr_overtime_rule_code_views.xml',
        'views/hr_overtime_rule_views.xml',
        'views/hr_overtime_reason_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/hr_overtime_request_mass_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 12.6,
    'currency': 'EUR',
    'license': 'OPL-1',
}
