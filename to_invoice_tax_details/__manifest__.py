{
    'name': "Invoice Tax Details",
    'name_vi_VN':"Chi Tiết Thuế Hóa Đơn",
    
    'summary': """
Show tax details on invoice lines
    """,
    'summary_vi_VN': """
Hiển thị chi tiết về thuế trên các dòng hoá đơn
    """,

    'description': """
The problem
===========
By default, Odoo gives you two options on how to display tax on invoice lines:

* Tax-Excluded: the subtotal WITHOUT tax included will be shown on invoice form view, PDF version
* Tax-Included: the subtotal WITH tax included will be shown on invoice form view, PDF version

There is no option to help you show both or even line's tax amount

The solution
============
This module offers an additional option "Tax Details" on Accounting Settings page to allow you to display the following for invoice lines of the invoice form view and invoice PDF version

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Vấn đề
======
Theo mặc định, Odoo cho bạn hai lựa chọn để hiển thị thuế trên các dòng hóa đơn:

* Tax-Excluded: Tổng phụ không bao gồm thuế sẽ được hiển thị trên form hóa đơn, bản PDF
* Tax-Included: Tôngt phụ bao gồm thuế sẽ được hiển thị trên form hóa đơn, bản PDF

Không có cách nào giúp bạn hiển thị cả hai hoặc cùng dòng giá trị thuế

Giải pháp
=========
Module này cung cấp thêm lựa chọn "Chi tiết thuế", cài đặt trong trang Kế Toán cho phép bạn hiển thị kèm theo các dòng hóa đơn của form hóa đơn và hóa đơn bản PDF

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/module_security.xml',
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': 'uninstall_hook',
}
