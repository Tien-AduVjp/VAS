# -*- encoding: utf-8 -*-

{
    'name': 'Maintenance - MRP',
    'name_vi_VN': 'Bảo trì - MRP',
    'summary': 'Schedule and manage maintenance on machine and tools.',
    'summary_vi_VN': 'Lập lịch và quản lý bảo trì máy móc và công cụ',
    'description': """
What it does
============
Schedule and manage maintenance on machine and tools in the Manufacturing module

Key features
============
- Preventive vs corrective maintenance
- Define different stages for your maintenance requests
- Plan maintenance requests (also recurring preventive)
- Manage equipments related to workcenters
- Track MTBF (Mean time between failures, MTTF (Mean time to failure), etc.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Mô tả
=====
Lập kế hoạch và quản lý bảo trì máy móc, công cụ trong phân hệ Sản xuất

Tính năng nổi bật
=================
- Bảo trì phòng ngừa vs Bảo trì khắc phục
- Xác định các giai đoạn khác nhau đối với các yêu cầu bảo trì
- Lập kế hoạch yêu cầu bảo trì (đồng thời phòng ngừa định kỳ)
- Quản lý các thiết bị liên quan đến năng lực sản xuất (Work center)
- Theo dõi MTBF (thời gian trung bình giữa 2 lỗi), MTTR (thời gian mắc lỗi trung bình),... 

Ấn bản được hỗ trợ
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
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '1.0',
    
    # any module necessary for this one to work correctly
    'depends': ['to_mrp_workorder', 'maintenance'],
    
    # always loaded
    'data': [
        'views/root_menu.xml',
        'views/maintenance_equipment_views.xml',
        'views/maintenance_request_views.xml',
        'views/mrp_workcenter_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
    ],
    'qweb': [
    ],
    # only loaded in demonstration mode
    'demo': ['data/mrp_maintenance_demo.xml'],
    'images': [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
