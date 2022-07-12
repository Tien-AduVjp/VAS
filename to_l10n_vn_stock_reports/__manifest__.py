{
    'name' : 'Vietnam Legal Stock Reports',
    'name_vi_VN' : 'Báo cáo Kho luật định Việt Nam',
    'version': '2.0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'support': 'apps.support@viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'summary': 'Warehouse Vietnam Legal Reports',
    'summary_vi_VN': 'Báo cáo Kho luật định Việt Nam',
    'sequence': 24,
    'category': 'Warehouse Management',
    'description':"""
Key Features
============
Add Warehouse Vietnam Legal Reports, include:

* Product Journal (S10-DN)
* General Inventory Journal (S11-DN)
* Stock-In Report
* Stock-Out Report
* Stock Card (S12-DN)

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng nổi bật
=================
Bổ sung Báo cáo Kho luật định Việt Nam, bao gồm:

 * Sổ chi tiết Vật liệu, Dụng cụ (SN10-DN)
 * Bảng kê Xuất - Nhập - Tồn (S11-DN)
 * Bảng kê Nhập kho hàng hóa
 * Bảng kê Xuất kho hàng hóa
 * Thẻ Kho (S12-DN)

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['to_stock_report_common', 'l10n_vn_common'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/stock_view.xml',
        'views/stock_report_view.xml',
        'views/report_common_templates.xml',
        'views/report_c200_s10dn.xml',
        'views/report_c200_s11dn.xml',
        'views/report_stockinout.xml',
        'views/report_c200_s12dn.xml',
        'wizard/l10n_vn_stock_inout_views.xml',
        'wizard/l10n_vn_c200_s10dn_views.xml',
        'wizard/l10n_vn_c200_s11dn_views.xml',
        'wizard/l10n_vn_c200_s12dn_views.xml',
        'views/account_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 198.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
