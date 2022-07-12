{
    'name': "Partner Employee Size",
    'name_vi_VN': 'Quy mô nhân viên của đối tác',
    'summary': """
Manage employee scale""",
    'summary_vi_VN': """
Thiết lập quy mô nhân viên của đối tác""",
    'description': """
Key features
============
* This module allows to set employee size for each partner.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
* Mô đun này cho phép thiết lập quy mô nhân viên trên từng đối tác.

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
    'category': 'Sales',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        'views/res_partner_employee_size_views.xml',
        'views/res_partner_views.xml',
        'security/ir.model.access.csv',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
