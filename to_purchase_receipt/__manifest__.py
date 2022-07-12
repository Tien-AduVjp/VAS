{
    'name': "Purchase Receipt from Purchase Order",
    'name_vi_VN': "Tạo Biên lai mua hàng từ Đơn mua",

    'summary': """
Create purchase receipts from purchase order""",
    'summary_vi_VN': """
Tạo biên lai mua hàng từ đơn mua""",

    'description': """
What it does
============
* This module allows purchasing staff to create purchase receipt from the Purchase Order screen, similar to create invoices from PO.
* If the PO already has an invoice, you cannot create a receipt and vice versa

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================

* Ứng dụng này cho phép nhân viên mua hàng tạo biên lai mua hàng từ màn hình PO, tương tự vói tạo hóa đơn từ PO.
* Nếu đơn mua đã có hóa đơn, bạn không thể tạo biên lai và ngược lại.
    
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
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'views/purchase_order_views.xml',
         ],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
