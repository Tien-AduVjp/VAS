# -*- coding: utf-8 -*-
{
    'name': "Employee Relatives",
    'name_vi_VN': 'Người thân của nhân viên',
    'summary': """
Store employee's relatives information""",
    'summary_vi_VN': """
Lưu trữ thông tin người thân của nhân viên""",
    'description': """
What it does
============
* Store employee's family and relatives information for unplanned circumstances.
* View in the "Employee" app when installed.

Key Features
============
* Easy input relatives information in the standard employee form. This information is only maintained and visible by users having the HR Officer role.
* Search for employees who have relatives or not.
* Filter Partners/Contacts to find out who are the relative of the company's employee.
* Search partners by related employee.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Lưu trữ thông tin gia đình và người thân của nhân viên cho các tình huống khẩn cấp.
* Nằm trong ứng dụng Nhân viên sau khi hoàn tất cài đặt.

Tính năng nổi bật
=================
* Dễ dàng nhập thông tin người thân trong mẫu nhân viên tiêu chuẩn. Thông tin này chỉ được duy trì và hiển thị bởi người dùng có vai trò Nhân viên Nhân sự.
* Tìm kiếm nhân viên có người thân hay không.
* Lọc Đối tác / Liên hệ để tìm ra ai là người thân của nhân viên công ty.
* Tìm kiếm đối tác của nhân viên liên quan.

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
    'category': 'Human Resources',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/hr_employee_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
