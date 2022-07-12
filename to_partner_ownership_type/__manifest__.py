{
    'name': "Partner Ownership Type",
    'name_vi_VN': 'Quản Lý Hình Thức Sở Hữu',
    'summary': """
Manage business ownership types""",
    'summary_vi_VN': """
Quản lý đối tác theo Hình thức sở hữu doanh nghiệp""",
    'description': """
Key Features
=============
* Add Business Ownership types on the Contact form. (Eg: Foreign Direct Investment, State Enterprises, Other Enterprises)
* Search Contacts by Ownership types.
* Manage ownership types.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
==================
* Thêm trường Hình thức sở hữu doanh nghiệp trên hồ sơ Liên hệ. (Ví dụ: Doanh nghiệp có vốn đầu tư nước ngoài, Doanh nghiệp nhà nước, Doanh nghiệp-đơn vị-tổ chức khác)
* Tìm kiếm Liên hệ theo hình thức sở hữu doanh nghiệp.
* Quản lý Đối tác theo các hình thức sở hữu doanh nghiệp.

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
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/ownership_type_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': 'pre_init_hook',
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
