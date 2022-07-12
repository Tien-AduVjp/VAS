# -*- coding: utf-8 -*-
{
    'name': "Subscription Management",
    'name_vi_VN': "Quản lý Thuê bao",

    'summary': """
Recurring invoicing, renewals""",

    'summary_vi_VN': """
Lập hóa đơn định kỳ, gia hạn""",

    'description': """
What it does
============
This module allows you to manage subscriptions.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cho phép bạn quản lý Thuê bao.

Tính năng chính
===============
    - Tạo và sửa Thuê bao
    - Điều chỉnh thuê bao với đơn bán
    - Tạo hóa đơn tự động trong khoảng thời gian cố định


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Camptocamp, Odoo S.A., T.V.T Marine Automation (aka TVTMA), Viindoo Technology",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'to_uom_subscription',
        'to_cost_revenue_deferred',
        'rating',
        'sale_management',
        'base_automation',
        ],

    # always loaded
    'data': [
        'data/cron_data.xml',
        'data/sale_subscription_data.xml',
        'data/mail_template_data.xml',
        'security/sale_subscription_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'wizard/sale_subscription_close_reason_wizard_views.xml',
        'wizard/sale_subscription_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/account_analytic_account_views.xml',
        'views/sale_subscription_close_reason_views.xml',
        'views/sale_subscription_views.xml',
        'views/sale_subscription_template_views.xml',
        'views/sale_subscription_stage_views.xml',
        'views/sale_subscription_automation_views.xml',
        'views/rating_views.xml',
        'views/digest_digest_views.xml',
        'views/res_config_settings_views.xml',
        'views/assets.xml',
        'views/subscription_portal_templates.xml',
        'views/rating_templates.xml',
        'report/sale_subscription_report_view.xml',
    ],
    'demo': [
        'demo/sale_subscription_demo.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 198.9,
    'subscription_price': 9.93,
    'currency': 'EUR',
    'license': 'OPL-1',
}
