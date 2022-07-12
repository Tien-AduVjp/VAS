{
    'name': 'Accounting & Finance',
    'name_vi_VN': 'Kế toán & Tài chính',
    'sequence': 35,
    'summary': 'Financial and Analytic Accounting',
    'summary_vi_VN': 'Kế toán tài chính, kế toán tổng hợp, kế toán quản trị',
    'description': """
Accounting Access Rights
========================
It gives the Administrator user access to all accounting features such as journal items and the chart of accounts.

It assigns manager and user access rights to the Administrator for the accounting application and only user rights to the Demo user.
""",
    'description_vi_VN': """
Quyền truy cập kế toán
======================
Cho phép người dùng Quản trị viên truy cập vào tất cả các tính năng kế toán như các mục nhật ký và biểu đồ tài khoản.

Chỉ định quyền truy cập của người quản lý và người dùng cho Quản trị viên đối với ứng dụng kế toán và chỉ quyền của người dùng đối với người dùng Demo.
""",

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/en/intro/accounting',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Accounting/Accounting',
    'version': '1.1.0',

    'depends': ['account', 'web_tour'],
    'data': [
        'data/menu_data.xml',
        'data/digest_data.xml',
        'security/account_accountant_security.xml',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/account_move_line_views.xml',
        'views/account_menuitem.xml',
        'views/assets.xml',
        'views/digest_views.xml',
        'views/account_fiscal_year_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_account_tag_views.xml',
        'views/account_group_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'wizard/account_change_lock_date.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'demo': ['data/demo_data.xml'],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 126.9,
    'subscription_price': 6.62,
    'currency': 'EUR',
    'license': 'OPL-1',
}
