{
    'name': 'Account Counterparts',
    'name_vi_VN': 'Đối ứng Tài khoản',
    'version': '1.0.2',
    'category': 'Accounting',
    'summary': """Counterpart relations between Journal Items""",
    'summary_vi_VN': """Liên kết đối ứng tài khoản cho các phát sinh kế toán""",
    'description': """
The Problem
===========

In Odoo, a single journal entry may contain multiple debit journal items and multiple credit journal items.
However, there is no way for us to identify the countered line(s) of a line and its countered account(s) which may causes some troubles when:

* making reports that require showing up counterparts and countered accounts of a transaction
* identifying types of business transactions. For example, according to Vietnam Accounting Standards, revenues from both loan interests and exchange
  rate profit are also encoded into the account 515. It is impossible to build Cash Flow Statement while it requires to separate those revenues.

Features at a glance
====================

+----+---------+--------------------+-------+--------+-------------------------+
| ID | Account | Countered Accounts | Debit | Credit | Countered Journal Items |
+----+---------+--------------------+-------+--------+-------------------------+
|  1 | 131     | 5111, 5113         |   150 |      0 | [2], [3]                |
+----+---------+--------------------+-------+--------+-------------------------+
|  2 | 5111    | 131                |     0 |    100 | [1]                     |
+----+---------+--------------------+-------+--------+-------------------------+
|  3 | 5113    | 131                |       |     50 | [1]                     |
+----+---------+--------------------+-------+--------+-------------------------+

Features in Details
===================

Journal Items
-------------
The following key stored and computed fields have been added into the Journal Item model (account.move.line):

* **Countered Journal Items**: the journal items that are counterparts of the current journal item.
* **Countered Accounts**: the accounts that are counterparts of the account of the current item.
* **Countered Amount**: The matched amount that has been set as countered amount for this journal item.
* **Countered Status**: A technical field to indicate that the journal item has either countered fully or partially or not-yet-countered.

Journal Entries
---------------
The following key stored and computed fields has been added into the Journal Entry model (account.move):

* **Countered Status**: A technical field to indicate that the journal entry has either countered fully or partially or not-yet-countered.

Wizards
-------
* **Counterparts Generator** is a wizard to allow accounting manager to either generate missing counterparts for account journal items or regenerate counterparts for all the existing items. It also allow you to limit the number of entries during generation by select one or more journals

Journal Item Counterparts
-------------------------
A new technical model named 'Journal Item Counterpart' (account.move.line.ctp) is created to map a credit journal item with a debit journal item which has the following key fields:

* **dr_aml_id**: The debit journal item (also known as 'account move line')
* **cr_aml_id**: The credit journal item
* **countered_amt**: the amount that match the counterpart operation of the two journal items above mention

When a counterpart operation is carried out, a new record of the model Journal Item Counterpart will
be created to map a credit journal item with a debit journal item to indicate that the later journal item is a counterpart with a countered amount.

Some Use Cases for Proof of Concepts
------------------------------------
* Entry with One single debit item and One single credit item

  * Entry:

    * [1] Debit 131 (Customer Receivable): $100
    * [2] Credit 511 (Sales Revenue): $100

  * Counterpart Mapping:

    * Debit Line: [1]
    * Credit Line: [2]
    * Countered Amount: $100

  * List view demostration:

    +----+---------+--------------------+-------+--------+------------------------+
    | ID | Account | Countered Accounts | Debit | Credit | Countered Journal Items|
    +----+---------+--------------------+-------+--------+------------------------+
    |  1 | 131     | 511                |   100 |      0 | [2]                    |
    +----+---------+--------------------+-------+--------+------------------------+
    |  2 | 511     | 131                |     0 |    100 | [1]                    |
    +----+---------+--------------------+-------+--------+------------------------+

* Entry with One single debit item and Multiple credit items

  * Entry:

    * [1] Debit 131 (Customer Receivable): $150
    * [2] Credit 5111 (Goods Sales Revenue): $100
    * [3] Credit 5113 (Service Sales Revenue): $50

  * Counterpart Mapping:

    * 1st Counterpart:

      * Debit Line: [1]
      * Credit Line: [2]
      * Countered Amount: $100

    * 2nd Counterpart:

      * Debit Line: [1]
      * Credit Line: [3]
      * Countered Amount: $50

  * List view demonstration

    +----+---------+--------------------+-------+--------+-------------------------+
    | ID | Account | Countered Accounts | Debit | Credit | Countered Journal Items |
    +----+---------+--------------------+-------+--------+-------------------------+
    |  1 | 131     | 5111, 5113         |   150 |      0 | [2], [3]                |
    +----+---------+--------------------+-------+--------+-------------------------+
    |  2 | 5111    | 131                |     0 |    100 | [1]                     |
    +----+---------+--------------------+-------+--------+-------------------------+
    |  3 | 5113    | 131                |       |     50 | [1]                     |
    +----+---------+--------------------+-------+--------+-------------------------+

* Entry with Multipe debit items and Multiple credit items

  * Entry:

    * [1] Debit 1311 (Customer Receivable): $120
    * [2] Debit 1312 (Customer Receivable): $30
    * [3] Credit 5111 (Goods Sales Revenue): $100
    * [4] Credit 5113 (Service Sales Revenue): $50

  * Counterpart Mapping:

    * 1st Counterpart:

      * Debit Line: [2]
      * Credit Line: [3]
      * Countered Amount: $20

    * 2nd Counterpart:

      * Debit Line: [2]
      * Credit Line: [4]
      * Countered Amount: $10

    * 3rd Counterpart:

      * Debit Line: [1]
      * Credit Line: [3]
      * Countered Amount: $80

    * 4th Counterpart:

      * Debit Line: [1]
      * Credit Line: [4]
      * Countered Amount: $40

  * List view demonstration

    +----+---------+--------------------+-------+--------+-------------------------+
    | ID | Account | Countered Accounts | Debit | Credit | Countered Journal Items |
    +----+---------+--------------------+-------+--------+-------------------------+
    |  1 | 1311    | 5111, 5113         |   120 |      0 | [3], [4]                |
    +----+---------+--------------------+-------+--------+-------------------------+
    |  2 | 1312    | 5113               |    30 |      0 | [4]                     |
    +----+---------+--------------------+-------+--------+-------------------------+
    |  3 | 5111    | 1311               |     0 |    100 | [1]                     |
    +----+---------+--------------------+-------+--------+-------------------------+
    |  4 | 5113    | 1311, 1312         |     0 |     50 | [1], [2]                |
    +----+---------+--------------------+-------+--------+-------------------------+

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Vấn đề
======

Trong Odoo, một bút toán sổ nhật ký có thể chứa nhiều phát sinh ghi nợ và ghi có.
Tuy nhiên, không có cách nào để xác định các dòng đối ứng của phát sinh và các tài khoản đối ứng của nó có thể gây ra một số rắc rối khi:

* lập báo cáo yêu cầu hiển thị các phát sinh với tài khoản đối ứng của phát sinh đó.
* xác định các loại giao dịch kinh doanh. Ví dụ, theo tiêu chuẩn Kế toán Việt Nam, doanh thu từ cả lãi cho vay và lãi tỷ giá cũng được định khoản vào tài khoản 515. Không thể xây dựng Báo cáo lưu chuyển tiền tệ trong khi phải tách các khoản thu đó.

Module này làm gì
=================

+----+-----------+--------------------+-------+--------+---------------------------+
| ID | Tài khoản | Tài khoản đối ứng  | Nợ    | Có     | Phát sinh kế toán đối ứng |
+----+-----------+--------------------+-------+--------+---------------------------+
|  1 | 131       | 5111, 5113         |   150 |      0 | [2], [3]                  |
+----+-----------+--------------------+-------+--------+---------------------------+
|  2 | 5111      | 131                |     0 |    100 | [1]                       |
+----+-----------+--------------------+-------+--------+---------------------------+
|  3 | 5113      | 131                |       |     50 | [1]                       |
+----+-----------+--------------------+-------+--------+---------------------------+

Tính năng chi tiết
==================

Sổ nhật ký
----------
Các trường tính toán và được lưu sau đây được thêm vào model phát sinh kế toán (account.move.line):

* **Phát sinh kế toán đối ứng**: các phát sinh kế toán đối ứng với phát sinh này.
* **Tài khoản đối ứng**: các tài khoản đối ứng với tài khoản của phát sinh này.
* **Giá trị đối ứng**: giá trị được được đặt làm giá trị đối ứng của phát sinh này.
* **Trạng thái đối ứng**: một trường kỹ thuật để phản ánh tình trạng của phát sinh đã được đối ứng hoàn toàn, một phần hay chưa được đối ứng.

Bút toán sổ nhật ký
-------------------
Các trường tính toán và được lưu sau đây được thêm vào model Bút toán sổ nhật ký (account.move):

* **Trạng thái đối ứng**: một trường kỹ thuật để phản ánh tình trạng của bút toán đã được đối ứng hoàn toàn, một phần hay chưa được đối ứng.

Tính năng
---------
* **Tạo liên kết đối ứng**  là  tính năng cho phép Kế toán trưởng tạo các đối ứng bị thiếu cho các phát sinh tài khoản hoặc tạo lại các đối ứng cho tất cả các phát sinh hiện có. Nó cũng cho phép giới hạn số lượng phát sinh khi tạo bằng cách chọn một hoặc nhiều sổ nhật ký.

Phát sinh đối ứng
-----------------
Một model kỹ thuật mới có tên 'Phát sinh kế toán đối ứng' (account.move.line.ctp) được tạo để ánh xạ một phát sinh bên có với một phát sinh bên nợ với các trường sau:

* **dr_aml_id**: Phát sinh bên nợ (còn được gọi là 'dòng phát sinh kế toán')
* **cr_aml_id**: Phát sinh bên có
* **countered_amt**: Số tiền tương ứng với đối ứng của hai mục nêu trên

Khi một thao tác đối ứng được thực hiện, một bản ghi mới của model phát sinh đối ứng được ghi nhận để ánh xạ một phát sinh có với một phát sinh nợ để chỉ ra sự đối ứng của hai phát sinh với giá trị tương ứng.

Một số tình huống ứng dụng
--------------------------
* Bút toán với một phát sinh bên nợ và một phát sinh bên có

    * Bút toán:

        * [1] Nợ 131 (Phải thu khách hàng): $100
        * [2] Có 511 (Doanh thu bán hàng): $100

    * Ảnh xạ đối ứng:

        * Dòng ghi nợ: [1]
        * Dòng ghi có: [2]
        * Giá trị đối ứng: $100

    * Bảng mô tả:

        +----+-----------+--------------------+-------+--------+------------------------+
        | TT | Tài khoản | Tài khoản đối ứng  | Bên nợ| Bên có | Phát sinh đối ứng      |
        +----+-----------+--------------------+-------+--------+------------------------+
        |  1 | 131       | 511                |   100 |      0 | [2]                    |
        +----+-----------+--------------------+-------+--------+------------------------+
        |  2 | 511       | 131                |     0 |    100 | [1]                    |
        +----+-----------+--------------------+-------+--------+------------------------+

* Bút toán với một phát sinh bên nợ và nhiều phát sinh bên có.

    * Bút toán:

        * [1] Nợ 131 (Phải thu khách hàng): $150
        * [2] Có 5111 (Doanh thu bán hàng hóa): $100
        * [3] Có 5113 (Doanh thu bán dịch vụ): $50

    * Ánh xạ đối ứng:

        * Đối ứng thứ nhất:

            * Dòng bên nợ: [1]
            * Dòng bên có: [2]
            * Giá trị đối ứng: $100

        * Đối ứng thứ hai:

            * Dòng bên nợ: [1]
            * Dòng bên có: [3]
            * Giá trị đối ứng: $50

    * Bảng mô tả

        +----+-----------+--------------------+-------+--------+-------------------+
        | TT | Tài khoản | Tài khoản đối ứng  | Nợ    | Có     | Phát sinh đối ứng |
        +----+-----------+--------------------+-------+--------+-------------------+
        |  1 | 131       | 5111, 5113         |   150 |      0 | [2], [3]          |
        +----+-----------+--------------------+-------+--------+-------------------+
        |  2 | 5111      | 131                |     0 |    100 | [1]               |
        +----+-----------+--------------------+-------+--------+-------------------+
        |  3 | 5113      | 131                |       |     50 | [1]               |
        +----+-----------+--------------------+-------+--------+-------------------+

* Bút toán với nhiều phát sinh bên nợ và nhiều phát sinh bên có:

    * Bút toán:

        * [1] Nợ 1311 (phải thu khách hàng): $120
        * [2] Nợ 1312 (phải thu khách hàng): $30
        * [3] Có 5111 (Doanh thu bán hàng hóa): $100
        * [4] Có 5113 (Doanh thu bán dịch vụ): $50

    * Ánh xạ đối ứng:

        * Đối ứng thứ nhất:

            * Dòng bên nợ: [2]
            * Dòng bên có: [3]
            * Giá trị đối ứng: $20

        *  Đối ứng thứ hai:

            * Dòng bên nợ: [2]
            * Dòng bên có: [4]
            * Giá trị đối ứng: $10

        * Đối ứng thứ ba:

            * Dòng bên nợ: [1]
            * Dòng bên có: [3]
            * Giá trị đối ứng: $80

        *  Đối ứng thứ tư:

            * Dòng bên nợ: [1]
            * Dòng bên có: [4]
            * Giá trị đối ứng: $40

    * Bảng mô tả

        +----+-----------+--------------------+-------+--------+-------------------+
        | TT | Tài khoản | Tài khoản đối ứng  | Nợ    | Có     | Phát sinh đối ứng |
        +----+-----------+--------------------+-------+--------+-------------------+
        |  1 | 1311      | 5111, 5113         |   120 |      0 | [3], [4]          |
        +----+-----------+--------------------+-------+--------+-------------------+
        |  2 | 1312      | 5113               |    30 |      0 | [4]               |
        +----+-----------+--------------------+-------+--------+-------------------+
        |  3 | 5111      | 1311               |     0 |    100 | [1]               |
        +----+-----------+--------------------+-------+--------+-------------------+
        |  4 | 5113      | 1311, 1312         |     0 |     50 | [1], [2]          |
        +----+-----------+--------------------+-------+--------+-------------------+

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'depends': [
        'viin_account_reconciliation',
    ],
    'data': [
        'data/scheduler_data.xml',
        'security/ir.model.access.csv',
        'views/account_move_line_ctp_views.xml',
        'views/account_move_line_view.xml',
        'views/account_move_view.xml',
        'wizard/wizard_account_counterpart_generator_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
