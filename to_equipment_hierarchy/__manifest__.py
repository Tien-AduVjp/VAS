# -*- coding: utf-8 -*-
{
    'name': "Equipment & Parts",
    
    'summary': """Manage equipments and parts in hierarchy structure.
        """,

    'summary_vi_VN': """Quản lý các thiết bị và các thành phần theo phân cấp phả hệ.
        """,

    'description': """
What it does
============
* An equipment could be apart of another equipment
* View equipment and its direct parts in the form
* View equipment and its recursive parts (parts of parts) in the form
* Search Equipment by Parts
* Search Parts by Equipment
* Groups parts by equipment

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Một thiết bị có thể là một phần của thiêt bị khác.
* Hiển thị thiết bị và các thành phần trực tiếp cũng như đệ quy của thiết bị đó trên giao diện.
* Tìm kiếm thiết bị từ các thành phần.
* Nhóm các phần theo thiết bị.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Operations/Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_maintenance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/maintenance_equipment_views.xml',
        'views/maintenance_request_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True, #TODO: Rework the code, separate 2 modules, one that depends on 'maintenance' and one that depends on 'hr_maintenance' when upgrading to a new version
    'application': False,
    'auto_install': True,
    'price': 49.5,
    'currency': 'EUR',
    'license': 'OPL-1',
}
