{
    'name': "Viin Cohort View",
    'name_vi_VN': "Viin Giao diện Cohort",
    'summary': "Basic Cohort view for Odoo Community Edition",
    'summary_vi_VN': "Giao diện Cohort cho Odoo Community Edition",
    'description': """

What it does
============
Basic Cohort view for Odoo Community Edition for others to extends

Key Features
------------
- Manage and analyze customer data according to the selected timeframe
- Group and filter data by different criteria
- Analyze customer retention

Example
-------

#. Analyze CRM Opportunities with cohort view

   .. code-block:: xml

     <record id="crm_lead_view_viin_cohort" model="ir.ui.view">
         <field name="name">crm.lead.view.viin_cohort</field>
         <field name="model">crm.lead</field>
         <field name="arch" type="xml">
             <viin_cohort string="Opportunities"
                 start_date="create_date" stop_date="date_closed" interval="week"
                 mode="churn" />
         </field>
     </record>

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Giao diện Cohort cho Odoo Community Edition cho các module khác mở rộng

Tính năng chính
---------------
- Quản lý, phân tích dữ liệu khách hàng trong khung thời gian đã chọn
- Nhóm và lọc dữ liệu theo nhiều tiêu chí
- Phân tích tỷ lệ giữ chân khách hàng

Ví dụ
-----
1. Phân tích Cơ hội kinh doanh với giao diện cohort

   .. code-block:: xml

     <record id="crm_lead_view_viin_cohort" model="ir.ui.view">
         <field name="name">crm.lead.view.viin_cohort</field>
         <field name="model">crm.lead</field>
         <field name="arch" type="xml">
             <viin_cohort string="Opportunities"
                 start_date="create_date" stop_date="date_closed" interval="week"
                 mode="churn" />
         </field>
     </record>

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['web'],
    'data': ['views/assets.xml'],
    'qweb': ['static/src/xml/viin_web_cohort.xml'],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 999.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
