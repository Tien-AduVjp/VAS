{
    'name': "Viin CRM",
    'name_vi_VN': "Viin CRM",
    'version': "1.0",
    'author': 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'category': "Sales/CRM",
    'summary': "Advanced features for CRM",
    'summary_vi_VN': "Cung cấp các tính năng nâng cao cho CRM",
    'description': """
Contains advanced features for CRM such as new views (e.g. Cohort, Dashboard, Map, etc)

Editions Supported
==================
1. Community Edition

    """,
    'description_vi_VN': """
Cung cấp các tính năng nâng cao cho CRM, các giao diện mới (vd: Cohort, Dashboard, Map, v.v.)

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,
    'depends': ['crm', 'viin_web_dashboard', 'viin_web_cohort', 'viin_web_map'],
    'data': [
        'views/crm_lead_views.xml',
        'report/crm_activity_report_views.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': ['crm'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
