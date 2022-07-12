{
    'name': "Viindoo Queue",
    'name_vi_VN': "",

    'summary': """
Implement job queue
        """,

    'summary_vi_VN': """

    	""",

    'description': """

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.0',
    'depends': ['mail'],
    'data': [
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/queue_views.xml',
        'views/queue_job_views.xml',
    ],
    'installable': False,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
