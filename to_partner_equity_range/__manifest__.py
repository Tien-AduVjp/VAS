{
    'name': "Partner Equity Range",
    'name_vi_VN': 'Quy mô vốn đối tác',
    'summary': """
Manage your partner's equity range""",
    'summary_vi_VN': """
Quản lý quy mô vốn của Đối tác""",
    'description': """
Key features
============
* Add the Partner's Equity Range field on the Contact form.
* Search Contacts by Equity Range.
* Manage your partner's equity range.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
* Thêm trường Quy mô vốn trên hồ sơ Liên hệ của công ty đối tác.
* Tìm kiếm Liên hệ theo Quy mô vốn của đối tác.
* Quản lý quy mô vốn của đối tác.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        'views/equity_range_views.xml',
        'views/res_partner_views.xml',
        'security/ir.model.access.csv'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': '_pre_init_to_partner_equity_range',
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
