{
    'name': "Delete Sales Order - Check Stock Transfer",
    'name_vi_VN': "Xoá Đơn Bán - Kiểm Tra Phiếu Kho",

    'summary': """
Disallow to delete a sale order, which is being referred by any related delivery (stock transfer).""",

    'summary_vi_VN': """
Không cho phép xóa đơn bán có phiếu kho liên quan.""",

    'description': """
What it does
============
Disallows the deletion on a sale order, which is being referred by any related stock transfer. In such case, the system will instead display a relevant message pop-up to notify the user.

Note: If you want to use this feature, you may enable it on Settings / Sales / Disallow to unlink SO relating Pickings.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Không cho phép xóa đơn bán có phiếu kho liên quan. Trong trường hợp trên, hệ thống sẽ hiển thị một cửa sổ thông báo tới người dùng.

Ghi chú: Nếu bạn muốn sử dụng chức năng này, bạn có thể bật nó trong phần Cài đặt / Bán hàng / Không cho phép xóa đơn bán/dòng đơn bán còn hóa đơn liên quan

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
