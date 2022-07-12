{
    'name': 'Mrp Workorder',
    'old_technical_name': 'mrp_workorder',
    'version': '1.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'category': 'Manufacturing',
    'sequence': 51,
    'summary': """Work Orders, Planing, Stock Reports.""",
    'depends': ['mrp'],
    'description': """
Key Features
============
Extension for MRP to support:

* Work order planning. Check planning grouped by production order / work center
* Traceability report

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    
    'description_vi_VN':"""
Tính năng nổi bật
=================
Mô-đun ```to_mrp_workorder``` bổ sung cho ứng dụng Sản xuất các tính năng:

* Lập kế hoạch Hoạt động sản xuất. Hoạch định sản xuất được nhóm theo Lệnh sản xuất/Năng lực sản xuất
* Lên báo cáo theo dõi Hoạt động sản xuất.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'data': [
        'views/mrp_production_views.xml',
        'views/mrp_workcenter_views.xml',
    ],
    'demo': [
        'data/mrp_production_demo.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
