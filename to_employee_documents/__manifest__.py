{
    'name': "Employee Documents",
    'name_vi_VN': "Tài liệu Nhân viên",

    'summary': """Manage employee documents and Notify before expire date""",
    'summary_vi_VN': """Quản lý tài liệu nhân viên và Gửi thông báo trước khi hết hạn""",

    'description': """
What it does
============
* "Employee Documents" module allow HR managers to manage all kinds of employee documents and automatically send an email notification when a document is about to get expired.
* You can find this module in the "Employee" app when installed.

Key Features
============
1. Document Types Management

    * HR Manager can define unlimited document types. For example, National ID Card, Insurance Card, Social Security Card, Passport, Visa, etc.
    * Each document type has the following properties:

        * Name: the name of the document type, which is unique in the system wide.
        * Days to Notify: the default value for number of days prior to the expiry for the system to notify about the expiration of the document of this type.
        * Description: text field to describe to type.
        * Kept by: An information field to indicated whether the original document of this type should be kept by the company or by the employee. It is a default value for the document of this type.
        * Return Upon Termination: The default value for the documents of this type to indicate if the origin of the document should be returned to its owner upon termination.

2. Employee Document

    * Is an Odoo document that allows HR Officer to manage all the documents related to the employees of the company.
    * Each document contains the following information.

        * Doc. Numer: the number/name of the document.
        * Kept By: An information field to indicated whether the original document is currently kept by the company or by the employee.
        * Return Upon Termination: If checked, the original document must be return to its owner. I.e. if the origin is kept by the company, it should be returned to the employee; if the origin is kept by the employee, it should be returned to the company.
        * Doc. Manager: the one in the HR department that takes responsibility for managing this document.
        * Document Type: Indicate the type of this document (e.g. SSI Card, Passport, etc).
        * Employee: the employee to whom this document is related.
        * Issue Date: the date on which the document was issued.
        * Issued By: linked to a partner record.
        * Place of Issue.
        * Expire Date: the date on which the document gets expired (if applicable).
        * Days to Notify: number of days to notify before the expiration of the document.
        * Image 1: store a photo of the document.
        * Image 2: store another photo of the document.
        * PDF: Store the PDF version of the Document.

    * PDF Viewer: the PDF version can be viewed online without downloads.

3. Employee

    * Show a stat button on the employee form to indicate number of documents related to this employee.
    * Click the button will drive the user to the list of the documents.
    * Employees can create/upload their own personal documents.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Mô đun "Tài liệu nhân viên" cho phép các nhà quản lý nhân sự quản lý các loại tài liệu nhân viên và tự động gửi email thông báo khi tài liệu này sắp hết hạn.
* Bạn có thể tìm thấy mô đun này tại ứng dụng "Nhân viên" sau khi hoàn tất cài đặt.

Tính năng nổi bật
=================
1. Quản lý các loại tài liệu

    * Nhà quản lý nhân sự có thể định nghĩa các loại tài liệu không giới hạn. Ví dụ như: Thẻ căn cước công dân, Sổ bảo hiểm, Thẻ An sinh Xã hội, Hộ chiếu, Thị thực.v.v
    * Mỗi loại tài liệu gồm có các thuộc tính dưới đây:

        * Tên: Đặt tên cho loại tài liệu và nên là tên duy nhất trên toàn hệ thống.
        * Số ngày báo trước: Số ngày trước ngày hết hạn để hệ thống thông báo cho nhân viên và người quản lý tài liệu về việc hết hạn. Nhập số không (0) để vô hiệu tính năng thông báo tự động.
        * Mô tả: Trường văn bản miêu tả loại tài liệu.
        * Giữ bởi: Trường thông tin cho phép chọn bản gốc của loại tài liệu này được công ty hay nhân viên lưu giữ.
        * Trả lại khi kết thúc hợp đồng hoặc khi tài liệu hết hạn (Return Upon Termination): Trường thông tin cho biết tài liệu gốc có được trả lại cho chủ sở hữu của nó khi chấm dứt hợp đồng hoặc khi tài liệu hết hạn hay không. Người dùng có thể tích chọn có hoặc không.

2. Tài liệu nhân viên

    * Là tài liệu Odoo cho phép cán bộ nhân sự quản lý tất cả tài liệu liên quan đến nhân sự của công ty.
    * Mỗi tài liệu chứa các thông tin sau:

        * Số tài liệu: Số/Tên của tài liệu.
        * Giữ bởi: Trường thông tin cho phép chọn bản gốc của loại tài liệu này được công ty hay nhân viên lưu giữ.
        * Trả lại khi kết thúc hợp đồng hoặc khi tài liệu hết hạn (Return Upon Termination): Trường thông tin cho biết tài liệu gốc có được trả lại cho chủ sở hữu của nó khi chấm dứt hợp đồng hoặc khi tài liệu hết hạn hay không. Người dùng có thể tích chọn có hoặc không.
        * Người quản lý tài liệu: Là người trong bộ phận Nhân sự chịu trách nhiệm quản lý tài liệu này.
        * Loại tài liệu: Cho biết loại của tài liệu này. (Ví dụ: Thẻ An sinh Xã hội, Hộ chiếu,v.v.)
        * Nhân viên: Nhân viên có liên quan đến tài liệu này.
        * Ngày cấp: Ngày tài liệu được cấp.
        * Được cấp bởi: Liên kết với một liên hệ được ghi trên hệ thống.
        * Nơi cấp
        * Ngày hết hạn: Ngày tài liệu hết hạn (Nếu có).
        * Số ngày báo trước: Số ngày trước ngày hết hạn để hệ thống thông báo cho nhân viên và người quản lý tài liệu về việc hết hạn.
        * Ảnh 1: Lưu trữ ảnh của tài liệu.
        * Ảnh 2: Lưu trữ ảnh khác của tài liệu.
        * PDF: Lưu trữ bản PDF của tài liệu.

    * Trình xem PDF: Bản PDF có thể được xem trực tuyến mà không cần tải về.

3. Nhân viên

    * Hiển thị nút thống kê trên biểu mẫu nhân viên để cho biết số lượng tài liệu liên quan đến nhân viên này.
    * Nhấp vào nút sẽ đưa người dùng đến danh sách các tài liệu.
    * Nhân viên có thể tạo / tải lên tài liệu cá nhân của riêng họ.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Employees',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', ],

    # always loaded
    'data': [
        'data/document_type_data.xml',
        'data/scheduler_data.xml',
        'data/mail_template_data.xml',
        'security/employee_document_security.xml',
        'security/ir.model.access.csv',
        'views/employee_document_views.xml',
        'views/employee_document_type_views.xml',
        'views/hr_employee_views.xml',
        ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
