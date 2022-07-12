# -*- coding: utf-8 -*-
{
    'name': "Hide Enterprise Modules - Website",
    'old_technical_name': 'to_hide_ent_modules_website_theme_install',

    'summary': """
Fix Apps action's domain when website is installed
""",

    'description': """
The module `to_hide_ent_modules` does the job of hiding Enterprise Modules very well until the module `website` is installed.
Once installed, the `website` overrides the action's domain with [!', ('name', '=like', 'theme_%')].

This module provides fixes by overriding the domain again with [('to_buy','=',False),'!', ('name', '=like', 'theme_%')]
    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_hide_ent_modules', 'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_module_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 4.5,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': "uninstall_hook",
}
