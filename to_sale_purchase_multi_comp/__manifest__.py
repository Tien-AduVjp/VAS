{
    'name': "Multi-Company Sale Purchase",

    'summary': """
Sale based on service outsourcing in multi company environment.""",

    'summary_vi_VN': """
Bán dịch vụ và outsource cho công ty khác trong môi trường đa công ty
    	""",

    'description': """
The problem
===========

Odoo offers a great module named `Sale Purchase` that support generated a purchase order upon validate a sales order based on
the switch `Purchase Automatically` on product model.

However, this field does not support multi-company environment. In other words, when a product is set with `Purchase Automatically`,
the policy will be applied to all the companies available in the database which is usually not what the users wants.

#. `Company A` sell `Product X` to its customer with `SO0001`, where the `Product X` is set with

   - `Purchase Automatically`: Yes
   - Vendor: Company B, which is another company in the same database
#. Upon `SO0001` confirmation, Odoo automaticaly generate a Purchase Order to Company B (e.g. `PO0001`)
#. In `Company B`, a sales user should create another sales order (e.g. `SO0002`) from `Company A` accordingly.
   Or, the `SO0002` could be generated automatically if you have an Inter-Cpmpany rule that helps generate a sales order from a purchase order in multi-company environment.
#. Upon `SO0002` confirmation, Odoo will try to generate another Purchase Order for the Company B to another
   vendor because the `Product X` is set with `Purchase Automatically`. This is usually NOT what the Company B wants. It is REALLY A PROBLEM! 

Solution
========

This module turn the field `Purchase Automatically` on product modeul into a company-specific field so that the `Company B` will be able turn it off
while the `Company A` will still be able to keep it on.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_purchase'],

    # always loaded
    'data': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': 'uninstall_hook',
}
