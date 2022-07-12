{
    'old_technical_name': 'to_partner_share_holder',
    'name': "Partner ShareHolder",
    'name_vi_VN': "Thông tin cổ đông của đối tác",
    'summary': """
Manage your partner's shareholder""",
    'summary_vi_VN': """
Quản lý thông tin cổ đông của đối tác""",
    'description': """
Key features
=============
* This module allows users to set up shareholder information on the Contact form, including:

  * Shareholder name
  * His/ her shareholding percentage.
  * Other related information of the shareholder.

* Search Contacts by the Partner's shareholders.
* Manage the information of the Partner's shareholders.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
* Cho phép thiết lập thông tin các Cổ đông của đối tác trên hồ sơ Liên hệ gồm:

  * Tên cổ đông.
  * Phần trăm sở hữu của từng cổ đông trong doanh nghiệp.
  * Những thông tin liên quan đến cổ đông đó đối với doanh nghiệp.

* Tìm kiếm Liên hệ theo thông tin cổ đông của doanh nghiệp.
* Quản lý thông tin cổ đông của đối tác.

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
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
