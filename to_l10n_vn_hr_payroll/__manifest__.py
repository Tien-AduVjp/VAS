{
    'name': "Vietnam - Payroll",
    'name_vi_VN': "Bảng lương Việt Nam",

    'summary': """Set up some salary information according to Vietnamese rules""",
    'summary_vi_VN': """
Thiết lập một số thông tin lương theo quy tắc Việt Nam
    	""",

    'description': """
What it does
============
The "Vietnam Payroll" module allows users to set up some salary information according to Vietnamese rules, including:

   * Payroll Contribution Type
   * Salary Rules
   * Personal Tax Rules

Key features
============
#. Update contribution rates for Payrol Contribution according to Vietnam's regulations (For Vietnamese companies). For example, some common types of salary contributions are:

   * Social Insurance
   * Health Insurance
   * Unemployment Insurance
   * Labor Union

#. Create available Personal Tax Rules according to Vietnam's regulations.

#. Automatically attach Personal Tax Rules according to Vietnam's regulations when creating new contracts for Vietnamese employees.

#. Adjusting the formulas of some Salary Rules according to Vietnamese standards.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô đun "Bảng lương Việt Nam" cho phép người dùng thiết lập một số thông tin lương theo quy tắc Việt Nam gồm:

   * Kiểu đăng ký đóng góp từ lương
   * Quy tắc lương
   * Quy tắc thuế TNCN

Tính năng nổi bật
=================
Mô đun này cho phép:

#. Cập nhật tỷ lệ đóng góp cho các kiểu đóng góp từ lương theo quy định của Việt Nam (Cho các công ty Việt Nam). Ví dụ một số kiểu đóng góp từ lương phổ biến như:

   * Bảo hiểm Xã hội
   * Bảo hiểm Y tế
   * Bảo hiểm thất nghiệp
   * Công đoàn

#. Tạo sẵn các Quy tắc thuế TNCN theo quy định của Việt Nam.

#. Tự động gắn Quy tắc thuế TNCN theo quy định của Việt Nam khi tạo mới hợp đồng cho nhân viên là người Việt Nam.

#. Điều chỉnh công thức của một số Quy tắc Lương theo chuẩn Việt Nam.

Ấn bản được hỗ trợ
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
    'category': 'Localization',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_payroll'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
