{
    'name': "Documents Management",
    'name_vi_VN': "Quản lý Tài liệu",

    'summary': """
Documents Management System""",

    'summary_vi_VN': """
Hệ thống Quản lý Tài liệu tập trung""",

    'description': """

What it does
============
This application allow you to archive, share or make schedule activity with your documents.

Key Features
============
* Archive, organize documents by workspace or tags were attached to documents.
* Share documents internal or public with your partners, customers.
* Automatic generate documents from other applications as project tasks, invoice...
* Create schedule activity for your documents.
* Permission for access and use documents in workspace by Team or User.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Mô tả
=====
Trước đây, các tài liệu đính kèm được tải lên và quản lý rải rác ở nhiều bản ghi thuộc các đối tượng khác nhau.
Với Ứng dụng này bạn có thể upload và quản lý tài liệu tập trung tại một chỗ.

Tính năng nổi bật
=================
* Cho phép thiết lập cây thư mục để quản lý tài liệu.
* Cho phép phân loại và tìm kiếm tài liệu phi cấu trúc bằng các sử dụng chức năng gắn thẻ.
* Cho phép thiết lập các hành động tự động trên tài liệu. Ví dụ: tự động đưa vào một thư mục bất kỳ, tự động thiết lập chủ sở hữu cho tài liệu,...
* Cho phép chia sẻ tài liệu nội bộ hoặc công khai với các đối tác.
* Cấu hình link hoạt để tích hợp với bất kỳ một phân hệ nào, từ đó cho phép tự động tạo tài liệu khi có một hoặc nhiều files đính kèm trên một bản ghi bất kỳ.
* Gắn sao và cho phép lọc ra các tài liệu có gắn sao.
* Phân quyền linh hoạt bằng cách tổ chức các teams với từng members trong team. Mỗi team hoặc member có quyền upload, đọc, sửa, xóa tài liệu của cả team hoặc của chính mình

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/apps/app/14.0/viin_document",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Productivity/Documents',
    'version': '0.1.0',
    'depends': ['to_base', 'mail', 'to_token_expiration'],
    'data': [
        'data/document_tag_category_data.xml',
        'data/document_tag_data.xml',
        'data/document_team_data.xml',
        'data/mail_activity_type_data.xml',
        'data/document_action_data.xml',
        'data/document_workspace_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/document_tag_category_views.xml',
        'views/document_tag_views.xml',
        'views/document_action_views.xml',
        'views/document_team_views.xml',
        'views/document_workspace_views.xml',
        'views/document_document_views.xml',
        'views/document_asset_templates.xml',
        'views/document_share_layout.xml',
        'views/document_share_views.xml',
        'wizard/document_run_manual_rule_wizard_view.xml',
        'views/document_auto_generate_rule.xml',
        'views/res_config_settings_views.xml'
    ],
    'demo': [
        'demo/document_document_demo.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': [
        'static/src/xml/document_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 899.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
