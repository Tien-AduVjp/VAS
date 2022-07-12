# -*- coding: utf-8 -*-
{
    'name': "HR Work Day Type",
    'name_vi_VN': "Kiểu ngày làm việc",
    'summary': """
Manage user defined workday types and their period""",
    'summary_vi_VN': """
Quản lý kiểu ngày làm việc và khoảng thời gian do người dùng định nghĩa""",
    'description': """

What it does
============

- By default, employees' working time is set as normal working day. Additional allowances will be manually calculated in case employees work overtime on weekend, holidays, etc.
- With this module, users can define different types of working days (e.g. normal working days, Tet holidays, etc), which can be used for other modules and applications.

Key Features
============

- Create, edit different types of workday (normal day, weekend, Tet holiday, etc) with the corresponding allowance rate percentage in *Settings > Technical > Resource > Work Day Types*
- Filter, search for workday types by name, duration, allowance rate, etc. 
- Serve as the basis for other applications to categorize working days

Supported Editions
==================

1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
- Thông thường, thời gian làm việc của nhân viên được mặc định tính là ngày làm việc bình thường. Nhân sự sẽ phải tự theo dõi và tính phần phụ cấp tăng thêm trong trường hợp nhân viên làm thêm giờ trong ngày lễ, Tết, v.v. 
- Với mô-đun này, người dùng có thể định nghĩa nhiều kiểu ngày làm việc (ví dụ ngày làm việc bình thường, ngày lễ Tết, v.v), từ đó lấy làm cơ sở thông tin cho các ứng dụng khác. 

Tính năng nổi bật
=================

- Thêm, chỉnh sửa loại ngày làm việc (ngày bình thường, ngày cuối tuần, ngày lễ Tết...) cùng phần trăm phụ cấp tương ứng trong mục *Cài đặt > Kỹ thuật > Nguồn lực > Kiểu ngày làm việc* 
- Phân loại, tìm kiếm các loại thời gian làm việc theo tên gọi, thời gian kéo dài, phần trăm phụ cấp, v.v.
- Là cơ sở cho các ứng dụng khác để phân loại ngày làm việc 

Ấn bản được hỗ trợ
==================

1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/work_day_type_data.xml',
        'views/work_day_type_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
