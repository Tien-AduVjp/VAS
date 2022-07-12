{
    'name' : 'Vietnam - General Ledger (S03a-DN)',
    'name_vi_VN': "Việt Nam - Sổ nhật ký chung (S03a-DN)",
    'version': '1.0.1',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Vietnam General Ledger according to the template S03a-DN',
    'summary_vi_VN': 'Sổ nhật ký chung Việt Nam theo mẫu S03a-DN',
    'sequence': 24,
    'category': 'Accounting',
    'description':"""
Vietnam Legal General Ledger Report
===================================

This application provides PDF and Excel version of the accounting general ledger that is in compliance with the Circular No. 200/2014/TT-BTC dated 22 December 2014 of the Ministry of Finance of Vietnam.

    """,
    'description_vi_VN': """
Mẫu sổ nhật ký chung Việt Nam
=============================
Ứng dụng này cung cấp phiên bản PDF and Excel của sổ sổ nhật ký chung tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính Việt Nam.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'depends': ['to_l10n_vn_qweb_layout'],
    'data': [
        'wizard/l10n_vn_c200_s03adn_views.xml',
        'views/account_report_view.xml',
        'views/report_c200_s03adn.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 198.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
