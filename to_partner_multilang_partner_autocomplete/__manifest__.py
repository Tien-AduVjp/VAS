{
    'name' : 'Partner Multilingual Partner Autocomplete',
    'name_vi_VN' : 'Tự động hoàn thành thông tin Đối tác đa ngôn ngữ',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': 'Translate Partners Name',
    'summary_vi_VN': 'Dịch tên đối tác',
    'sequence': 30,
    'category': 'Technical Settings',
    'description':"""
    """,
    'depends': ['to_partner_multilang', 'partner_autocomplete'],
    'data': [
        'views/assets.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
