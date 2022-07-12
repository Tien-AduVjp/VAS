# -*- coding: utf-8 -*-
{
    'name': "Maintenance Approval",
    'name_vi_VN': "Phê duyệt sửa chữa",

    'summary': """
Allow employees create maintenance approval requests and submit to managers to approve.  
""",

    'summary_vi_VN': """
Cho phép nhân viên tạo yêu cầu phê duyệt sửa chữa và gửi tới quản lý để được phê duyệt.
    	""",

    'description': """
Key Features
============
* Managers can configurate the Maintenance approval with 4 types of validation: No validation, Approval Officer, Manager, Manager and Approval Officer. 
* Employees create a maintenance request for products with:

   * Equipment needs repairing (optional, the equipment has to be selected when the last manager approved).
   * Error description (required).

* Managers can 'Confirm' or 'Refuse' the request.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng chính
===============
* Người quản lý có thể thiết lập 4 kiểu phê duyệt: Không cần xác nhận, Cán bộ phê duyệt, Quản lý trực tiếp, Quản lý trực tiếp và Cán bộ phê duyệt.
* Nhân viên tạo một yêu cầu sửa chữa cho sản phẩm với:

   * Thiết bị cần sửa chữa (không bắt buộc, chỉ đến khi bộ phận cuối cùng duyệt thì bắt buộc phải chọn thiết bị)
   * Mô tả lỗi (bắt buộc)

* Người quản lý có thể Duyệt hoặc Từ chối yêu cầu

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations/Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_approvals', 'hr_maintenance'],

    # always loaded
    'data': [
        'views/approval_request_views.xml',
        'views/maintenance_request_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'post_init_hook': 'post_init_hook',
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
