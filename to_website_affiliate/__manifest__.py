# -*- coding: utf-8 -*-
{
    'name': "Website Affiliate",
    'name_vi_VN': "",
    'version': '1.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Manage Share Links, Commissions and Payment Request on website',
    'summary_vi_VN': 'Quản lý chia sẻ liên kết, Hoa hồng và Yêu cầu Thanh toán trên website',
    'category': 'Sales',
    'description':"""
Key Features
============
* **Manage Link Sharing**: An affiliate can create links using their affiliate codes to share with their friends or customers.
* **Manage Affiliate Commissions**: An affiliate can see all their affiliate commission details (commission name, date, amount, status)
* **Manage Affiliate Payment Request**: An affiliate can see all their payment request. They can also create new payment request(s) if their total unpaid commission is greater than Minimum Payout

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng nổi bật
=================
* **Quản lý chia sẻ liên kết**: Một cộng tác viên có thể tạo liên kết khi dùng mã cộng tác viên của họ để chia sẻ với bạn bè hoặc khách hàng của họ.
* **Quản lý hoa hồng cho cộng tác viên**: Một cộng tác viên có thể nhìn thấy tất cả các khoản hoa hồng của họ (tên khoản hoa hồng, ngày tháng, số lượng và trạng thái)
* **Quản lý yêu cầu thanh toán**: Một cộng tác viên có thể thấy tất cả các yêu cầu thanh toán của họ. Họ có thể tạo yêu cầu thanh toán mới nếu tổng số hoa hồng chưa được thanh toán lớn hơn Khoản tối thiểu.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    
    'depends': ['website_sale', 'to_affiliate_sale', 'link_tracker'],
    'data': [
        'views/assets.xml',
        'data/data_menu.xml',
        'views/website_template.xml',
        'views/website_views.xml',
        'views/link_tracker.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
