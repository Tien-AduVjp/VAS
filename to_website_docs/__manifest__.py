{
    'name': "Website Documentation",
    'name_vi_VN': "Tài liệu Trực tuyến",
    
    'summary': """
Documentation Management System for Odoo Websites""",
    'summary_vi_VN': """
Hệ thống quản ý tài liệu trên Website Odoo""",

    'description': """
What it does
============
Document Management for Odoo Websites

1. In Website GUI

    - Create category, document and anchors
    - Edit name of document, category
    - Confirm, approve document
    - Published, unpublished document, category
    - Delete document, category
    - Sort document, category
    - Add tags to document
    - Quick search document
    - Change image and color cover of category

2. Access right:

    Include 4 Access right: Editor, Reviewer, Designer, Manager

    2.1 Editor:

        - Create documents/contents
        - Allow Edit of Document/Content if Assigned and its status is 'Draft'/'Confirmed'/'Reject'
        - Allow Delete of Document/Content if Assigned, is the author and its status is 'Draft'/'Confirmed'/'Reject'
    
    2.2 Reviewer:

        - Includes Editor's rights
        - Allow create/edit Category (Do not publish / unpublish)
        - Change the cover image and background color for the category
        - Edit/Delete Editor's Document

    2.3 Designer:

        - Includes Content Moderator rights
        - Allow to publish Documents/Contents/Categories
        - Edit/Delete Reviewer's Document

    2.4 Manager

        - Full access right

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Quản Lý tài liệu trên Websites Odoo
===================================
1. Giao diện trên Website

    - Tạo chuyên mục, tài liệu và liên kết(link/anchors)
    - Chỉnh sửa tên chuyên mục, tài liệu
    - Xác nhận / Phê duyệt tài liệu
    - Xuất bản / Dừng xuất bản chuyên mục và tài liệu
    - Xóa chuyên mục và tài liệu
    - Sắp xếp thứ tự chuyên mục và tài liệu
    - Thêm thẻ cho tài liệu
    - Tìm kiếm nhanh tài liệu
    - Thay đổi hình bìa và màu nền cho chuyên mục
    
2. Phân quyền

    Gồm 4 quyền phân cấp: Biên tập viên (Editor), Người kiểm duyệt nội dung (Reviewer), Biên tập và thiết kế (Designer), Quản lý (Manager)

    2.1 Biên tập viên (Editor):

        - Tạo các tài liệu và nội dung cho tài liệu
        - Cho phép chỉnh sửa Tài liệu/Nội dung nếu được Phân công và trạng thái của liệu/Nội dung đấy là 'Dự thảo' / 'Xác nhận', 'Bị từ chối'
        - Cho phép xóa Tài liệu/Nội dung nếu được Phân công, là tác giả và trạng thái của liệu/Nội dung đấy là 'Dự thảo' / 'Xác nhận', 'Bị từ chối'
    
    2.2 Người kiểm duyệt nội dung (Reviewer):

        - Bao gồm các quyền của Biên tập viên
        - Cho phép tạo/sửa Chuyên mục (Không được xuất bản / hủy xuất bản)
        - Thay đổi hình bìa và màu nền cho chuyên mục
        - Chỉnh sửa/Xóa Tài liệu của Biên tập viên

    2.3 Biên tập và thiết kế (Designer):

        - Bao gồm các quyền của Người kiểm duyệt nội dung
        - Cho phép publish Tài liệu/Nội dung/Chuyên mục
        - Chỉnh sửa/Xóa Tài liệu của Người kiểm duyệt nội dung

    2.4 Quản lý(Manager)

        - Có đầy đủ quyền

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    'category': 'Website/Documentation',
    'version': '0.1.2',
    'depends': ['to_website_base', 'rating'],
    'data': [
        'data/website_menu_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/website_doc_tag_views.xml',
        'views/website_doc_category_views.xml',
        'views/website_document_views.xml',
        'views/website_document_content_views.xml',
        'views/assets.xml',
        'views/snippets.xml',
        'views/templates.xml',
        'wizard/wizard_website_document_merge_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': ['static/src/xml/qweb.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
