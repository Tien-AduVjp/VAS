{
    'name': "Time-Off Custom",
    'name_vi_VN': "Tùy Chỉnh Thời Gian Xin Nghỉ",

    'summary': """
Allows you to choose a time period if you create time-off in several days
""",

    'summary_vi_VN': """
Cho phép chọn khoảng thời gian nếu bạn xin nghỉ trong nhiều ngày
    	""",

    'description': """

What it does
============
- By default, if employees create time-off in several days, the default time will be all of those days. Example: If an employee wants to create time-off from 13:00 1/1/2021 to 12:00 1/3/2021, he will have to create many requests with the same reason.
- This module allows employees to custom a time period when they create time-off for several days at once.

Key Features
============
- Allow users to select particular time-off (half-day/ by hours) when submitting a time-off request rather than the day-count default. 
- Allow users to request several days off at once. 

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Mô tả
=====
- Theo mặc định, nếu nhân viên xin nghỉ trong nhiều ngày liên tục, hệ thống sẽ tính thời gian nghỉ là toàn bộ những ngày đó. Ví dụ: Nếu muốn tạo xin nghỉ từ 13h ngày 1/1/2021 đến 12h ngày 3/1/2021, nhân viên sẽ phải tạo xin nghỉ nhiều lần với cùng một lý do.
- Mô-đun này cho phép nhân viên chọn khoảng thời gian tùy ý khi tạo đề nghị xin nghỉ nhiều ngày liên tục trong 1 lần

Tính năng nổi bật
=================
- Cho phép người dùng xin nghỉ theo khoảng thời gian tùy ý (nghỉ nửa ngày/ nghỉ theo giờ) thay vì đơn vị nghỉ theo ngày như mặc định.
- Cho phép người dùng xin nghỉ nhiều ngày cùng lúc chỉ với một lần tạo yêu cầu. 

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
    'category': 'Human Resources/Time Off',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_holidays'],

    # always loaded;,;
    'data': [
        'views/hr_leave_views.xml',
        'wizards/adjust_leave_views.xml',
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
