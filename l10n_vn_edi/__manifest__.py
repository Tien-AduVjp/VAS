{
    'name': 'E-Invoice common',
    'old_technical_name': 'viin_l10n_vn_einvoice_common',
    'name_vi_VN': 'Thông tin chung của hóa đơn điện tử',

    'summary': """
Some common fields of e-Invoice
    """,
    'summary_vi_VN': """
Một số trường chung của hóa đơn điện tử
    """,

    'description': """
What it does
============
Add some common fields of e-invoice

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Thêm một số trường chung cho hóa đơn điện tử

Ấn bản được Hỗ trợ
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
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0.6',

    # any module necessary for this one to work correctly
    'depends': ['account_edi', 'to_vietnamese_number2words', 'to_legal_invoice_number', 'to_base', 'l10n_vn_common', 'viin_reverse_move_line'],
    'data': [
        'security/ir.model.access.csv',
        'security/module_security.xml',
        'wizard/account_einvoice_error_notification_views.xml',
        'wizard/account_invoice_einvoice_cancel_views.xml',
        'wizard/account_invoice_einvoice_adjustment_views.xml',
        'data/account_einvoice_type_data.xml',
        'data/account_einvoice_template_data.xml',
        'data/scheduler_data.xml',
        'data/account_edi_format_data.xml',
        'data/vn_edi_templates.xml',
        'views/root_menu.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'views/account_journal_dashboard.xml',
        'views/account_portal_templates.xml',
        'views/account_einvoice_serial_views.xml',
        'views/einvoice_service_views.xml',
        'views/account_einvoice_template_views.xml',
        'views/account_einvoice_type_views.xml',
        'views/assets.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
