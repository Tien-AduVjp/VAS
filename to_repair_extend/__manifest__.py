# -*- coding: utf-8 -*-
{
    'name': "Repair Report",
    'name_vi_VN': "Báo Cáo Sửa Chữa",
    'summary': """
Add more information on repair orders and new comprehensive repair report
    """,
    'summary_vi_VN': """
Thêm thông tin về đơn sửa chữa và báo cáo sửa chữa toàn diện
    """,
    'description': """
What it does
============
This module adds more information on repair orders and build new comprehensive repair report

Key features
============
* This module adds some additional information fields such as:

  * Supervisor
  * Customer feedback
  * Forecast (used to note the forecast time for repair schedule)

* Add Repair Analysis Report with filters, groups in many criterias such as:

  * Repair history of products by produt lot and serial numbers
  * Supervisor, Customer
  * Date, location, repair status
  * Quantity or value of part products, repair products
  * etc.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này bổ sung thêm một số trường thông tin trên đơn sửa chữa và xây dựng báo cáo phân tích chi tiết các hoạt động sửa chữa

Tính năng nổi bật
=================
* Khi cài mô-đun này, trên lệnh sửa chữa sẽ xuất hiện thêm một số trường thông tin như:

  * Người giám sát
  * Phản hồi khách hàng
  * Dự báo thời gian cần bảo trì tiếp theo

* Tạo thêm Báo cáo Phân tích Sửa chữa với các bộ lọc, nhóm theo nhiều tiêu chí như:

  * Lịch sử sửa chữa của sản phẩm theo số lô, series
  * Người giám sát, Khách hàng
  * Thời gian, địa điểm, tình trạng sửa chữa
  * Số lượng hoặc giá trị các sản phẩm phụ tùng, sản phẩm sửa chữa
  * v.v

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['repair', 'stock', 'to_repair_access_group'],
    'old_technical_name': 'to_mrp_repair_extend',

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'report/repair_report.xml',
        'views/repair_report_views.xml',
        'views/repair_views.xml',
        'views/stock_production_lot_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
