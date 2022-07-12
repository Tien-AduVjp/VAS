# -*- coding: utf-8 -*-
{
    'name': "Cash Flow Forecast",
    'name_vi_VN': 'Dự Báo Dòng Tiền',
    'summary': """Generate forecast for cash flow""",
    'summary_vi_VN': """Tạo dự báo cho dòng tiền""",
    'description': """
What it does
============
Cash Flow Forecast is a module for Odoo that allows generating forecast for cash flow.

* Add your cash flow
* See all cash in/out in detailed reports
* Export a report to Excel

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Dự Báo Dòng Tiền là một mô-đun cho Odoo cho phép tạo dự báo cho dòng tiền.

* Thêm dòng tiền của bạn
* Xem tất cả tiền vào/ra trong các báo cáo chi tiết
* Xuất báo cáo sang Excel

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/cash_flow_user_input_view.xml',
        'views/cash_flow_forecast_report.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
