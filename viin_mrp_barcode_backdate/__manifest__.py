{
    'name': 'MRP Barcode - Backdate',
    'name_vi_VN': 'Mã vạch sản xuất - Thời gian quá khứ',
    
    'summary': 'MRP Barcode - Backdate',
    'summary_vi_VN': 'Mã vạch sản xuất - Thời gian quá khứ',
    
    'description': """
What it does
============
* Bridge between MRP Barcode and Backdate
* Add context to button on view to open backdate wizard

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
* Mô đun cầu nối giữa Mã vạch sản xuất và Thời gian quá khứ
* Thêm ngữ cảnh cho nút trên giao diện để mở cừa sổ thời gian quá khứ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    'category': 'Hidden',
    'version': '1.0',

    'depends': ['to_mrp_barcode', 'to_mrp_backdate'],

    'data': [
        'views/mrp_workorder_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
