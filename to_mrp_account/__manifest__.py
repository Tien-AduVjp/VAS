{
    'name': 'Advanced MRP Accounting',
    'name_vi_VN': 'Phân tích chi phí sản xuất',
    'version': '1.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Manufacturing',
    'summary': 'Accounting Integration for Manufacturing',
    'summary_vi_VN': """Tích hợp kế toán và sản xuất""",
    'description': """
What it does
============

- This module allows for accurate tracking of product costs and production batch costs
- From there, users can have the basis for calculating cost, sales price, and profit

Key Features
============

- Automatically generate production cost analysis
- Analyse production costs according to raw material costs
- Analyse material cost by production batch
- Track the total cost of raw materials and the unit cost of finished products

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====

- Mô-đun này cho phép theo dõi chính xác chi phí cấu thành nên sản phẩm và chi phí của lô sản xuất
- Từ đó cơ sở đề tính giá vốn, giá bán và lợi nhuận

Tính năng nổi bật
=================

- Tự động tạo bảng phân tích chi phí sản xuất
- Phân tích chi phí sản xuất theo chi phí nguyên vật liệu cấu thành sản phẩm
- Phân tích chi phí nguyên vật liệu theo lô sản sản xuất
- Theo dõi tổng chi phí nguyên vật liệu và chi phí đơn chiếc của thành phẩm

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['mrp_account'],
    'data': [
        'views/mrp_production_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'reports/cost_structure_report.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
