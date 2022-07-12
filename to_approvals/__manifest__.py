# -*- coding: utf-8 -*-
{
    'name': "Approvals",
    'name_vi_VN': "Phê duyệt",

    'summary': """
Submit Approval Requests to get approved
    """,

    'summary_vi_VN': """
Trình duyệt để được phê duyệt
    """,

    'description': """
What it does
============
This module is a base for the development of other approval modules: Procurement approval, Maintenance approval, Timesheet approval, Overtime Approval

* Manager can create approval types with 4 selections: No Validation, Approval Officer, Manager, Manager and Approval Officer.
* Employee can create approval requests.
* Team leader can see the request of their own employees.
* Followers who are usual employees can only see the request.

Key Features
============
* When the employee clicks the confirm button, a notification message will be sent to the first approver.
* After the first approver approves, a notification message will be sent to the second approver (if the request needs double validation) or send notification for the employee (if the request just validates once).
* After the second approver validates, a notification message will be sent to the employees who created it.
* When the request is done, a notification message will be sent to the employee who created it.
* If the request is refused, a notification message will be sent to the employee who created it

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Đây là mô-đun chung để phục vụ cho việc phát triển các mô-đun Đề nghị khác: Đề nghị cung ứng, Đề nghị sửa chữa, Đề nghị chấm công, Đề nghị tăng ca...

* Người quản lý có thể tạo loại đề nghị với 4 lựa chọn: Không cần xác nhận, Cán bộ phê duyệt, Quản lý trực tiếp, Quản lý trực tiếp và Cán bộ phê duyệt.
* Nhân viên có thể tạo yêu cầu đề nghị.
* Quản lý trực tiếp có thể xem các đơn đề nghị của các nhân viên mình quản lý.
* Người theo dõi là nhân viên bình thường chỉ có thế xem yêu cầu.

Tính năng nổi bật
=================
* Sau khi người tạo yêu cầu bấm xác nhận, hệ thống sẽ gửi thông báo đến Người phê duyệt lần 1.
* Sau khi Người phê duyệt lần 1 bấm duyệt, hệ thống sẽ gửi thông báo đến người phê duyệt lần 2 (nếu cần phê duyệt 2 lần) hoặc thông báo cho người tạo yêu cầu (nếu chỉ phê duyệt 1 lần).
* Sau khi Người phê duyệt lần 2 bấm duyệt: một thông báo sẽ được gửi đến người tạo đơn.
* Khi đơn đề nghị được hoàn thành, một thông báo sẽ được gửi đến người tạo đơn.
* Nếu yêu cầu bị từ chối, một thông báo sẽ được gửi đến người tạo đơn.

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
    'category': 'Human Resources/Approvals',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_org_chart'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'data/ir_sequence_data.xml',
        'views/root_menu.xml',
        'views/approval_request_views.xml',
        'views/approval_request_type_views.xml',
    ],
    # only loaded in demonstration mode 
    'demo': [
        'demo/res_users_demo.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
