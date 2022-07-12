{
    'name': "Survey Printing",

    'name_vi_VN': "In ngay tại trang khảo sát",

    'summary': """
        Allows to print survey page in print, test, public mode.
    """,

    'summary_vi_VN': """
        Cho phép in trang khảo sát trong chế độ in, kiểm thử, công khai.
    """,

    'description': """

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Marketing/Survey',
    'version': '0.1.0',

    'depends': ['survey'],

    'data': [
        'views/assets.xml',
        'templates/survey_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
