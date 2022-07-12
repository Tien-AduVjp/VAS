{
    'name' : 'Vietnam Chart of Accounts - Circular No. 200/2014/TT-BTC',
    'name_vi_VN' : 'Hệ thống Tài khoản Thông tư 200/2014/TT-BTC',
    'version' : '1.0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Vietnam Chart of Accounts according to Circular #200/2014/TT-BTC by the Ministry of Finance',
    'summary_vi_VN': 'Hoạch đồ kế toán Việt Nam theo thông tư 200/2014/TT-BTC',
    'category' : 'Localization',
    'sequence': 11,
    'description': """
Vietnam Chart of Accounts - Circular No. 200/2014/TT-BTC
========================================================
* fixed l10n_vn module to get fully compliant with the Circular #200/2014/TT-BTC dated Dec 22, 2014 by the Ministry of Finance which came into force on Jan 1, 2015
* partially in compliance with the Circular #133/2016/TT-BTC dated Aug 26, 2016 by the Ministry of Finance which came into force on Jan 1, 2017.
* More common taxes (e.g. import, export, special consumption, nature resource usage, etc)
* Complete Chart of Accounts
* Add one more field named code to the model account.account.tag so that Vietnamese accountants can use it the way of parent view account (like what was before Odoo 9). This brings peace to the accountants.
* New account tags data has been added to use in the similar way of parent view accounts before Odoo 9. For example, accountant now can group all accounts 111xxx using account the tag 111.
* Accounts now link to the tags having corresponding code. E.g. account 1111 and 1112 .... 111x have the same account tag of 111.
* Several analytic tags that is required by financial reports are added
* Add English translations to bring ease for worldwide developers and foreigners doing business in Vietnam. Translations will be loaded upon installation of l10n_multilang module

For more information on the full list of accounts, please visit https://erponline.vn/blog/blogs-5/vietnam-chart-of-accounts-under-the-vietnamese-accounting-standards-99

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
'description_vi_VN': """
Hoạch đồ kế toán Việt Nam theo thông tư 200/2014/TT-BTC
========================================================
* Mô-đun l10n_vn tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính bắt đầu có hiệu lực t ngày 1 tháng 1 năm 2015
* Tuân thủ một phần Thông tư số 133/2016 / TT-BTC ngày 26 tháng 8 năm 2016 của Bộ Tài chính bắt đầu có hiệu lực t ngày 1 tháng 1 năm 2017
* Các loại thuế được bổ sung (ví dụ: thuế nhập khẩu, thuế xuất khẩu, thuế tiêu thụ đặc biệt, thuế tài nguyên môi tr, v.v.)
* Hệ thống tài khoản đầy đủon
* Thêm một trường có tên mã vào tài khoản model.account.tag để kế toán Việt Nam có thể sử dụng nó theo cách của tài khoản cha chỉ xem (giống như trước đây của Odoo 9). Việc này thuận lợi hơn cho kế toán viên.
* Dữ liệu thẻ tài khoản mới đã được thêm vào để sử dụng theo cách tương tự với các tài khoản kiểu ch trước Odoo 9. Ví dụ: kế toán hiện có thể nhóm tất cả các tài khoản 111xxx bằng tài khoản thẻ 111.
* Tài khoản hiện liên kết đến các thẻ có mã tương ứng. Ví dụ. tài khoản 1111 và 1112 .... 111x có cùng thẻ tài khoản 111.
* Một số thẻ phân tích kế toán được được thêm vào phục vụ cho báo cáo tài chính
* Thêm bản dịch tiếng Anh để thuận tiện cho các nhà phát triển trên toàn thế giới và người nước ngoài kinh doanh tại Việt Nam. Các bản dịch sẽ được tải khi cài đặt mô-đun l10n_multilang

Để biết thêm thông tin về danh sách đầy đủ các tài khoản, vui lòng truy cập https://erponline.vn/blog/blogs-5/vietnam-chart-of-accounts-under-the-vietnamese-accounting-standards-99

Phiên bản hỗ trợ
==================
1. Community Edition
2. Enterprise Edition

""",
    'depends' : ['l10n_vn', 'to_account_financial_income', 'to_account_income_deduct', 'to_tax_is_vat'],
    'data' : [
            # update chart of accounts
            'data/account_analytic_tag_data.xml',
            'data/account_group.xml',
            'data/account_tag.xml',
            'data/account_tax_report_line_data.xml',
            'data/account_tax.xml',
            'data/account_chart.xml',
            'data/l10n_vn_chart_post_data.xml',
      ],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}

