{
    'name' : 'Cost & Revenue Deferral',
    'name_vi_VN': "Phân Bổ Chi Phí & Doanh Thu",
    'version': '1.0.2',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Automate deferred costs and revenues entries',
    'summary_vi_VN': 'Tự động hóa các bút toán phân bổ chi phí và doanh thu',
    'sequence': 30,
    'category': 'Accounting & Finance',
    'description':"""
What is does
============
1. This allows you to manage the cost and revenue recognition on buying / selling products.
2. It keeps track of the installments occurred on those cost / revenue recognitions, and creates account moves for those installment lines.

Key Features
============

1. Define deferred revenue types

    * Define deferred revenue types

        * Name: the name of the type for identification purpose
        * Journal: the default journal for account moves of the deferred revenues in this type
        * Deferred Account: The account for encoding deferred revenues
        * Revenue Account
        * Disposal Account
        * Analytic account
        * Analytic Tags
        * Time Method

            * Number of Defferals

                * Number of Deferrals
                * One Entry Every

            * Ending Date
 
                * One Entry Every
                * Ending Date

    * Define deferred cost types

        * Name: the name of the type for identification purpose
        * Journal: the default journal for account moves of the deferred costs in this type
        * Deferred Account: The account for encoding (prepaid) expense that will be deferred as costs.
        * Recognition Account: An account to store recognition moves. It is usually a cost account
        * Disposal Account
        * Analytic account
        * Analytic Tags
        * Time Method

            * Number of Defferals

                * Number of Deferrals
                * One Entry Every

            * Ending Date

                * One Entry Every
                * Ending Date

2. Revenue Deferral: manage revenue deferrals

    * Name: the name of the deferral
    * Category
    * Value
    * Salvage Value
    * Residual Value
    * Deferral Board
    * Journal Items / Entries

3. Cost Deferral

    * Name: the name of the deferral
    * Category
    * Value
    * Salvage Value
    * Residual Value
    * Deferral Board
    * Journal Items / Entries

4. Mass generation of Journal Entries for cost/revenue Recognitions

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    
    'description_vi_VN': """
Module này làm gì
=================
1. Module này cho phép bạn quản lý ghi nhận chi phí và doanh thu khi mua / bán sản phẩm.
2. Nó theo dõi các khoản giải ngân đã xảy ra trên các ghi nhận chi phí / doanh thu đó và tạo ra các bút toán kế toán cho các dòng giải ngân đó.

Tính năng chính
===============

1. Xác định các loại phân bổ doanh thu

    * Xác định các loại phân bổ doanh thu

        * Tên: tên loại cho mục đích nhận diện
        * Sổ nhật ký: sổ nhật ký mặc định cho các bút toán kế toán của phân bổ doanh thu trong loại này
        * Tài khoản Phân bổ: Tài khoản để ghi nhận phân bổ doanh thu
        * Tài khoản Doanh thu
        * Tài khoản Thanh lý
        * Tài khoản Quản trị
        * Thẻ TK Quản trị
        * Phương thức kết chuyển

            * Số lần trả trước

                * Số lần trả trước
                * Số bút toán trên mỗi lần trả trước

            * Ngày kết thúc

                * Số bút toán cho đến ngày kết thúc
                * Ngày kết thúc

    * Định nghĩa các loại phân bổ chi phí

        * Tên: tên loại cho mục đích nhận diện
        * Sổ nhật ký: sổ nhật ký mặc định cho các các bút toán của phân bổ chi phí trong loại này
        * Tài khoản Phân bổ: Tài khoản cho chi phí trả trước sẽ được phân bổ dưới dạng chi phí.
        * Tài khoản Ghi nhận: Một tài khoản để lưu trữ các bút toán ghi nhận. Nó thường là một tài khoản chi phí
        * Tài khoản Thanh lý
        * Tài khoản Quản trị
        * Thẻ TK Quản trị
        * Phương thức kết chuyển

            * Số lần trả trước

                * Số lần trả trước
                * Số bút toán trên mỗi lần trả trước
 
            * Ngày kết thúc
 
                * Số bút toán cho đến ngày kết thúc
                * Ngày kết thúc

2. Phân bổ Doanh thu: quản lý phân bổ doanh thu

    * Tên: tên của phân bổ doanh thu
    * Danh mục
    * Giá trị
    * Giá trị vãn hồi
    * Giá trị còn lại
    * Bảng phân bổ doanh thu
    * Phát sinh / Bút toán Kế toán

3. Phân bổ Chi phí

    * Tên: tên của phân bổ chi phí
    * Danh mục
    * Giá trị
    * Giá trị vãn hồi
    * Giá trị còn lại
    * Bảng phân bổ chi phí
    * Phát sinh / Bút toán Kế toán

4. Tạo hàng loạt các Bút toán Kế toán để ghi nhận chi phí / doanh thu

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    
    'depends': ['account'],
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/deferral_category_view.xml',
        'wizard/deferral_disposal_view.xml',
        'wizard/deferral_confirm_view.xml',
        'views/deferral_view.xml',
        'views/account_move_line_view.xml',
        'views/product_template_view.xml',
        'data/scheduler_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
