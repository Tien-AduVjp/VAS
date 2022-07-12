# -*- coding: utf-8 -*-
{
    'name': "Purchase Confirmation Backdate",
    'name_vi_VN': "Xác nhận Mua hàng trong quá khứ",
    'summary': """
Validate/Approve purchase orders with backdate""",
    'summary_vi_VN': """
Phê duyệt/ xác nhận đơn mua với ngày giao nhận trong quá khứ""",

    'description': """

Key Features
============
By default, when you validate or approve a purchase order, Odoo will take the current date and time for the Confirmation Date. This is sometimes not what you want, especially when you want to validate the purchase order which was actually confirmed in the past. This module, on the other hand, enable users to confirm purchase orders with backdate by updating the Confirmation Date field in order to input your desired confirmation date

Backdate Operations Control
---------------------------
By default, only users of the group "Purchase / Administrator" will be able to carry out backdate operations in the Purchase application. Other users must be granted the access group Backdate Operations before they can do so.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """

Tính năng nổi bật
================
Theo mặc định, khi bạn xác thực hoặc phê duyệt đơn đặt hàng, Odoo sẽ lấy ngày giờ hiện tại cho Ngày xác nhận đơn mua. Điều này đôi lúc sẽ gây bất tiện cho người dùng, đặc biệt là khi bạn muốn xác thực đơn đặt hàng đã được xác nhận trong quá khứ.Ứng dụng này sẽ giúp người dùng có thể xác nhận một đơn mua với ngày xác nhận trong quá khứ. Khi xác nhận đơn mua, màn hình hiển thị cửa sổ cho phép chọn ngày xác nhận đơn mua trong quá khứ. 

Phân quyền
----------
Theo mặc định, chỉ người dùng nằm trong nhóm “Mua/ Quản trị viên” mới có thể thực hiện thao tác này. Những người dùng khác phải được cấp quyền mới sử dụng tính năng này.

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
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations/Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'to_backdate'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'wizard/wizard_confirm_purchase_views.xml',
        'views/purchase_order_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
