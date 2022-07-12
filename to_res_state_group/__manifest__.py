{
    'name': "Country State Group",
    'name_vi_VN': "Nhóm Vùng Miền",

    'summary': """
Categorize country states and partners in different state groups
""",

    'summary_vi_VN': """
Phân loại các bang / tỉnh và đối tác vào các vùng / miền khác nhau
    	""",

    'description': """
Key Features
============
This module categorize partners and country states in different state groups (also known as Country Regions),
This module is to add data of Vietnamese geographic regions.

What it does
============

#. State Group: A new data model that contains the following fields

   * Name: the name of the state group (e.g. Northwest, Red River Delta, etc)
   * Parent: the parent group to which the group belongs. This helps build state group hierarchy
   * Country: the country to which the group belongs
   * States: the country states that belong to the state group.

#. Country State:

   * State Group: a new field added to create relationship between Country State and State Group

#. Partner:

   * State Group: a new field added to create relationship between Country State and State Group which is related to the partner's state

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============
Module này phân loại các đối tác và các vùng miền vào các nhóm vùng khác nhau (còn được gọi là Vùng Quốc Gia),
Mô-đun này để thêm dữ liệu về các vùng miền ở Việt Nam.

Mô tả
=====

#. Vùng/Miền: Là một kiểu mới chứa các trường sau

   * Tên: Tên của vùng/miền (vd. Northwest, Red River Delta, v.v)
   * Vùng/Miền cấp trên: Vùng/Miền cấp trên mà vùng/miền hiện hành thuộc về. Điều này giúp tổ chức phân cấp vùng/miền
   * Quốc gia: Quốc gia mà vùng miền thuộc về
   * Bang/Tỉnh: các bang/tỉnh thuộc vùng/miền này.

#. Bang/Tỉnh:

   * Vùng/Miền: thêm trường mới để tạo quan hệ giữa bang/tỉnh và vùng/miền

#. Đối tác:

   * Vùng/Miền: thêm trường mới để tạo quan hệ giữa bang/tỉnh và vùng/miền của đối tác

Ấn bản hỗ trợ
==================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        'data/res.state.group.csv',
        'security/ir.model.access.csv',
        'views/res_country_state_views.xml',
        'views/res_partner_views.xml',
        'views/res_state_group_views.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png',
        'static/description/vietnam_state_group.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
