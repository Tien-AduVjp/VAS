{
    'name': "Manufacturing Backdate",
    'name_vi_VN': "Sản Xuất Trong Quá Khứ",

    'summary': """
MRP backdate operations, incl. posting inventory, mark MO as done, backdate work orders""",

    'summary_vi_VN': """
Nhập ngày trong quá khứ cho các hoạt động Sản xuất (hoàn thành lệnh, hoạt động sản xuất trong quá khứ, bút toán kho cho hoạt động sản xuất trong quá khứ)
    	""",

    'description': """
What it does
=============
This module enables customers to manage the backdate for operations in Manufacturing

Key features
============

* Posting inventory with backdate
* Inventory Accounting with backdate
* Work Orders with backdate

  * **Start** a work order with backdate
  * **Pause** a work order with backdate
  * **Block or Unblock** a work order with backdate
  * **Finish** a work order with backdate

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này cho phép khách hàng quản lý ngày giao nhận trong quá khứ cho các hoạt động Sản xuất

Tính năng nổi bật
=================
* Vào sổ nhập kho thành phẩm từ lệnh sản xuất với ngày trong quá khứ
* Bút toán kế toán kho cho nguyên vật liệu và thành phẩm (bao gồm cả bán thành phẩm)
* Hoạt động sản xuất

  * **Khởi động** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Tạm dừng** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Khóa hoặc thôi khóa** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Hoàn thành** một hoạt động sản xuất với ngày giờ trong quá khứ

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
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp', 'to_stock_backdate'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'wizard/mrp_markdone_backdate_wizard_views.xml',
        'wizard/mrp_workcenter_block_view.xml',
        'wizard/mrp_workorder_backdate_wizard_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
