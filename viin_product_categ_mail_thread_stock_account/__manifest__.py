{
    'name': "Product Category Chatter - Stock Account",
    'name_vi_VN':"Theo dõi thay đổi Nhóm sản phẩm - Kế toán kho",

    'summary': """
Integrate Product Category Chatter with WMS Accounting
""",

    'summary_vi_VN': """
Tích hợp Product Category Chatter với Kế toán kho
    """,

    'description': """
Key Features
============
Integrate Product Category Chatter with WMS Accounting, allows to track changes of the following field of the product category

   * property_stock_account_input_categ_id
   * property_stock_account_output_categ_id
   * property_stock_valuation_account_id
   * property_stock_journal
   * property_cost_method
   * property_valuation
   * removal_strategy_id

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
Tích hợp Product Category Chatter với Kế toán kho, cho phép theo dõi sự thay đổi của các trường sau của Nhóm sản phẩm

   * property_stock_account_input_categ_id
   * property_stock_account_output_categ_id
   * property_stock_valuation_account_id
   * property_stock_journal
   * property_cost_method
   * property_valuation
   * removal_strategy_id

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
    'category': 'Sales/Sales',
    'version': '0.1',
    'depends': ['viin_product_categ_mail_thread', 'stock_account'],
    'images' : [
        'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
