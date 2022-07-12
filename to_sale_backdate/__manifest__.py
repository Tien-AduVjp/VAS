{
    'name': "Sales Confirmation Backdate",
    'name_vi_VN': "Xác nhận Bán hàng trong quá khứ",

    'summary': """
Confirm sales with backdate""",

    'description': """
The problem
===========

* By default, when you click Confirm Sale, Odoo will take the current date and time for the Confirmation Date field.
* This behavior is sometimes not what you want when you do the job for the orders that were actually confirmed in the past.

The solution
============

This application allows confirm sales orders with backdate by popping out a wizard with Confirmation Date field to give you
a chance to input your desired confirmation date

Backdate Operations Control
---------------------------

By default, only users of the group "Sales / User: All Documents" can carry out backdate operations in Sales application.
Other users must be granted to the access group **Backdate Operations** before she or he can do it.

Supported Edition
------------------
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Vấn đề
======
* Theo mặc định, Odoo sẽ tự động áp dụng thời gian hiện tại khi bạn xác nhận đơn bán.
* Điều này, đôi khi không như bạn mong muốn. Ví dụ: bạn nhập dữ liệu cho đơn bán đã được xác nhận trong quá khứ.

Giải pháp
=========
* Mô - đun này cho phép lùi thời điểm xác nhận đơn bán trong quá khứ bằng cách bật lên trường Xác nhận đơn bán để bạn thay đổi thời gian trong quá khứ

Kiểm soát hoạt động lùi ngày
----------------------------
* Theo mặc định, chỉ những người dùng được phân quyền Có thể nhìn thấy tất cả các tài liệu trong ứng dụng Bán hàng mới có thể thực hiện thao tác lùi ngày trong quá khứ cho đơn bán đã xác nhận. Những người dùng khác phải được cấp quyền truy cập nhóm Cập nhật ngày quá khứ trước khi có thể thực hiện thao tác này.

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
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'to_backdate'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/wizard_confirm_sale_views.xml',
    ],
    'images': ['static/images/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
