{
    'name': "Time-Off Custom",
    'name_vi_VN': "Tùy Chỉnh Thời Gian Nghỉ",

    'summary': """
Time-off Customization, Time-Off Report in detail
""",

    'summary_vi_VN': """
Tùy biến kế hoạch nghỉ, báo cáo nghỉ chi tiết
""",

    'description': """
What it does
============
This module provides some extra features like:

* Customize multi-day time-off with flexible times
* Time-off adjustment, which has been approved
* Time-off report by day

Key Features
============
#. Customize time-off

   * By default, if employees create time-off in several days, the default time will be all of those days. Example: If an employee wants to create time-off from 13:00 1/1/2021 to 12:00 1/3/2021, he will have to create many requests with the same reason.
   * This module allows employees to custom a time period when they create time-off for several days at once.

#. Time-off adjustment

   * Allows time-off period adjustment of employees, which has been approved.

#. Time-off report by day

   * Provide employee detailed time-off information by each day according to many criteria such as leave type, status, department, ...

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này cung cấp thêm một số tính năng bổ sung như:

* Tùy chỉnh thời gian nghỉ trong nhiều ngày với thời gian linh hoạt
* Thay đổi Thời gian nghỉ, cái mà đã được phê duyệt
* Báo cáo nghỉ theo từng ngày

Tính năng nổi bật
=================
#. Tùy chỉnh thời gian nghỉ

   * Theo mặc định, nếu nhân viên xin nghỉ trong nhiều ngày liên tục, hệ thống sẽ tính thời gian nghỉ là toàn bộ những ngày đó. Ví dụ: Nếu muốn tạo xin nghỉ từ 13h ngày 1/1/2021 đến 12h ngày 3/1/2021, nhân viên sẽ phải tạo xin nghỉ nhiều lần với cùng một lý do.
   * Mô-đun này cho phép nhân viên chọn khoảng thời gian tùy ý khi tạo đề nghị xin nghỉ nhiều ngày liên tục trong 1 lần

#. Thay đổi Thời gian nghỉ

   * Cho phép điều chỉnh khoảng thời gian xin nghỉ của nhân viên, cái mà đã được duyệt.

#. Báo cáo nghỉ theo từng ngày

   * Cung cấp thông tin nghỉ chi tiết của nhân viên theo từng ngày theo nhiều tiêu chí như kiểu nghỉ, trạng thái, phòng ban, ...

Ấn bản được Hỗ trợ
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
    'category': 'Human Resources/Time Off',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_holidays'],

    # always loaded;,;
    'data': [
        'security/ir.model.access.csv',
        'views/hr_leave_views.xml',
        'wizards/adjust_leave_views.xml',
        'reports/hr_leave_detail_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
