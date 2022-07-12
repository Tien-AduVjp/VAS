# -*- coding: utf-8 -*-
{
    'name': "Maintenance Equipment Hierarchy",
    'name_vi_VN': "Phân cấp thiết bị bảo trì",
    
    'summary': """Show all the emaintenance requests of the equipments and its parts on production lot form
        """,

    'summary_vi_VN': """Hiển thị danh sách bảo trì của thiết bị và các thiết bị con của chúng trên giao diện Lô - Seri
        """,

    'description': """
What it does
============
* On Production Lot form, show all the maintenance requests of the equipments and its parts

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Trên giao diện Lô - Seri, hiển thị danh sách các yêu cầu bảo trì của thiết bị gắn với số lô - seri này, trong đó có bao gồm
cả các yêu cầu bảo trì của các thiết bị con của nó.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'http://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_stock_equipment', 'to_equipment_hierarchy'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_production_lot_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
