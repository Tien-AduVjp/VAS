# -*- coding: utf-8 -*-
{
    'name': "Hide Enterprise Modules - Fix website_theme_install",

    'summary': """
Fix website_theme_install action's domain
""",

    'description': """
The module `to_hide_ent_modules` does the job of hiding Enterprise Modules very well until the module `website_theme_install` is installed.
Once installed, the `website_theme_install` overrides the action's domain with [!', ('name', '=like', 'theme_%')].

This module provides fixes by override the domain again with [('to_buy','=',False),'!', ('name', '=like', 'theme_%')]
    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_hide_ent_modules', 'website_theme_install'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_module_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 4.5,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': "uninstall_hook",
}
