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

* Manager can create approval types with multiple approvers.
* Employee can create approval requests.
* Team leader can see the request of their own employees.
* Followers who are usual employees can only see the request.

Key Features
============
* When the employee clicks the confirm button, a notification message will be sent to the next approver.
* Request approval will be reviewed and approved in sequence by those on the list of approvers
* Request approval is in accepted state if the number of approvers is equal to or greater than the minimum number of consents which must include those marked "required".
* Request approval is in decline if at least one person is marked "required" to reject, or the number of rejected votes is greater than the number reviewers minus the minimum
* When the request is done, a notification message will be sent to the employee who created it.
* If the request is refused, a notification message will be sent to the employee who created it.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Đây là mô-đun chung để phục vụ cho việc phát triển các mô-đun Đề nghị khác: Đề nghị cung ứng, Đề nghị sửa chữa, Đề nghị chấm công, Đề nghị tăng ca...

* Người quản lý có thể tạo loại đề nghị với lựa chọn nhiều cấp phê duyệt.
* Nhân viên có thể tạo yêu cầu đề nghị.
* Quản lý trực tiếp có thể xem các đơn đề nghị của các nhân viên mình quản lý.
* Người theo dõi là nhân viên bình thường chỉ có thế xem yêu cầu.

Tính năng nổi bật
=================
* Sau khi người tạo yêu cầu bấm xác nhận, hệ thống sẽ gửi thông báo đến người duyệt tiếp theo trong danh sách phê duyệt.
* Đề nghị trình duyệt sẽ được xem và phê duyệt theo trình tự bởi những người trong danh sách phê duyệt.
* Trình duyệt ở trạng thái được chấp nhận nếu số  người chấp thuận bằng hoặc lớn hơn số chấp thuận tối thiểu trong đó phải bao gồm những người được đánh dấu "được yêu cầu".
* Trình duyệt ở trạng thái từ chối nếu có ít nhất một người được đánh dấu "được yêu cầu" từ chối hoặc số phiếu từ chối lớn hơn số người trong danh sách duyệt trừ đi số tối thiểu.
* Khi đơn đề nghị được hoàn thành, một thông báo sẽ được gửi đến người tạo đơn.
* Nếu yêu cầu bị từ chối, một thông báo sẽ được gửi đến người tạo đơn.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com/apps/app/14.0/to_approvals",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Approvals',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'data/ir_sequence_data.xml',
        'views/root_menu.xml',
        'views/abstract_approval_user_line_views.xml',
        'views/approval_request_views.xml',
        'views/approval_request_type_views.xml',
    ],

    # only loaded in demonstration mode
    'demo':[
        'demo/res_user_demo.xml',
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
