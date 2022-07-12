{
    'name': 'Quality Control for MRP',
    'name_vi_VN': 'Quản lý chất lượng sản xuất',
    'summary': 'Quality Management with MRP',
    'summary_vi_VN': 'Tích hợp quản lý chất lượng với sản xuất',
    'description': """
What it does
============

- To help users monitor the quality of finished products, this module allows integrating the post-production quality control feature into the Manufacturing application.
- This feature helps enterprises streamline production processes, and ensure finished products meet the enterprise’s quality standards.
- In addition, this module provides the means to create a long-term set of quality control criteria, ensuring the highest quality of everything from raw materials to quality control processes. Problems and defects from inferior materials are excluded.

Key Features
============

- Receive quality warnings before and after completing manufacturing orders, and generate test orders corresponding to the warnings.
- Allow creating Quality Check Order; Quality control criteria from which to schedule next Actions to correct and prevent
- Create and keep track of stock orders during the production quality check
- Automatically generate reports related to quality control, production quality alerts, and analysis for next actions
- Set up a set of rules to control and evaluate the output quality of products

Editions Supported
==================
1. Community Edition

    """,
    'description_vi_VN': """
Mô tả
=====

- Nhằm theo dõi chất lượng thành phẩm sau sản xuất, mô-đun này cho phép tích hợp tính năng kiểm soát chất lượng thành phẩm sau sản xuất.
- Tính năng này giúp các công ty giúp hợp lý hoá sản xuất và đảm bảo các sản phẩm cuối cùng đáp ứng các tiêu chuẩn chất lượng của công ty.
- Bên cạnh đó, mô-đung này còn cung cấp phương tiện để tạo ra một bộ tiêu chí kiểm soát chất lượng lâu dài, đảm bảo rằng tất cả mọi thứ, từ nguyên liệu đến quy trình kiểm tra đều có chất lượng cao nhất. Các vấn đề và khiếm khuyết từ các vật liệu kém chất lượng đều bị loại trừ.

Tính năng nổi bật
=================

- Tiếp nhận thông tin cảnh báo chất lượng từ trước và sau khi hoàn thành lệnh sản xuất và tạo các lệnh kiểm tra tương ứng các cảnh báo. 
- Cho phép tạo Lệnh kiểm tra chất lượng; Tiêu chí kiểm tra chất lượng từ đó thiết lập các Hành động kế tiếp để khắc phục và ngăn ngừa.
- Tạo và theo dõi các phiếu kho cần xử lý, phiếu kho đã hoàn thành được phát sinh trong quá trình kiểm tra chất lượng sản xuất.
- Tự động tạo các báo cáo liên quan tới kiểm tra, cảnh báo chất lượng sản xuất và phân tích các hành động kế tiếp.
- Thiết lập bộ quy tắc kiểm soát và đánh giá chất lượng đầu ra của sản phẩm.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,
    'old_technical_name': 'quality_mrp',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    
    'version': '1.0',
    'category': 'Quality',
    'sequence': 50,
    
    'depends': ['to_quality_stock', 'to_mrp_workorder'],
    
    "data": [
        'security/module_security.xml',
        'views/quality_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
        'views/mrp_workcenter_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    "demo": ['data/quality_mrp_demo.xml'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
