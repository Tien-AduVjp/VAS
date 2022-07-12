{
    'name': 'Assets Management',
    'name_vi_VN': 'Quản lý Tài sản Kế toán',
    'old_technical_name': 'account_asset',
    'summary': """Manage your account assets and generate depreciations automatically""",
    'summary_vi_VN': """Quản lý tài sản kế toán và tự động tạo bút toán khấu hao""",
    'depends': ['to_enterprice_marks_account'],
    'description': """
What it does
============
Manage assets owned by a company or a person; Keep track of depreciations and create corresponding journal entries.

Key Features
============

* Allow to create Asset Types and configure rules for each type (depreciation method, time method, number of entries, journal entries, etc.)
* Available depreciation periodicity:

  * Depreciate according to a predetermined number of entries with a predetermined periodicity
  * Depreciate until a predetermined date with a predetermined periodicity
    
* Available depreciation methods:

  * Linear
  * Degressive (with a predetermined Degressive factor)
  * Accelerated Degressive

* Automatically create assets when validating asset purchase invoices
* Automatically depreciate with no limit on the number of assets
* Compliant with Vietnamese accounting standards on depreciation of fixed assets and value allocation of equipments.
  This feature requires the availability of module `to_l10n_vn_account_asset`.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Quản lý tài sản thuộc sở hữu của một công ty hoặc một người; Theo dõi các khoản khấu hao và tạo các bút toán tương ứng.

Tính năng nổi bật
=================

* Cho phép tạo các Kiểu tài sản và cấu hình sẵn quy tắc cho từng kiểu (phương pháp tính toán, số lần khấu hao, ngày khấu hao,
  bút toán sổ nhật ký,...)
* Hỗ trợ các tiêu thức trích khấu hao sau:

  * Khấu hao theo số lần định trước với chu kỳ định trước
  * Khấu hao cho đến ngày định trước với chu kỳ định trước

* Hỗ trợ các phương pháp khấu hao:

  * Đường thẳng
  * Lũy thoái (với hệ số lũy thoái được định trước)
  * Khấu hao nhanh

* Tự động tạo tài sản khi xác nhận hoá đơn mua tài sản
* Tự động trích khấu hao không hạn chế số lượng tài sản
* Tương thích với chuẩn mực kế toán Việt Nam về trích khấu hao TSCĐ và phân bổ giá trị Công cụ dụng cụ.
  Tính năng này cần có module `to_l10n_vn_account_asset`

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author' : 'Odoo S.A., T.V.T Marine Automation (aka TVTMA)',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'category': 'Accounting/Accounting',
    'version': '1.1.0',
    'sequence': 32,
    'data': [
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'wizard/asset_depreciation_confirmation_wizard_views.xml',
        'wizard/asset_modify_views.xml',
        'wizard/asset_revaluation_views.xml',
        'wizard/account_asset_asset_add_wizard.xml',
        'wizard/asset_sell_wizard.xml',
        'wizard/asset_dispose_wizard.xml',
        'views/account_asset_category_views.xml',
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
        'views/account_asset_templates.xml',
        'views/product_views.xml',
        'views/res_config_settings_views.xml',
        'report/account_asset_report_views.xml',
        'data/account_asset_data.xml',
    ],
    'qweb': [
        "static/src/xml/account_asset_template.xml",
    ],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 189.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
