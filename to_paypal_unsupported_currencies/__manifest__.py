{
    'name': "Paypal - Unsupported Currency Support",
    'name_vi_VN': "Paypal - Hỗ trợ tiền tệ không tiêu chuẩn",

    'summary': """
Pay unsupported currencies with Paypal""",

    'summary_vi_VN': """
Thanh toán Paypal cho các khoản tiền tệ không nằm trong danh mục tiền tệ được Paypal hỗ trợ
    	""",

    'description': """
The problem
===========
* Paypal supports a limited number of currencies, which causes problems when your customers pay their invoices in a currency that does not supported by Paypal.
* Here is the list of currencies that are supported by Paypal: https://developer.paypal.com/docs/api/reference/currency-codes/

What this module does
=====================
* When customer carries out payment in a currency that is not supported by PayPal, this module will convert the payment amount into an amount in a currency (which is configurable) that is supported by Paypal before sending the payment data to Paypal.
* During payment processing and payment notification, this module ensures that the converted amount is equivalent to the original one for full reconciliation.
* During reconciliation, the difference due to exchange rate will be encoded into the exchange rate journal.

Example
-------
* Assume that

   * The company currency is VND (Viet Nam Dong - đ), which is not a currency supported by Paypal
   * Invoice INV/2019/0001 is amounted 2,000,010đ (in VND)
   * The Paypal acquirer is configured with USD as the default currency for conversion in this case
   * Exchange rate between VND/USD: 23,100

* Payment process

   * Convert VND to USD: 2,000,010  / 23,100 = 86.580519481, and will be rounded into 86.58
   * Request Paypal to process payment for the $86.58
   * After processing, Paypal notifies Odoo with success processing of the amount of $86.58.
   * Odoo verifies this amount and generates a payment of $86.58 and posted with value of $86.58 * 23,100 = 1,999,998đ
   * During reconciliation, the difference of 12đ (between 1,999,998đ and 2,000,010đ) will be encoded into the exchange rate difference. The corresponding invoice will be set to paid.

    """,
    'description_vi_VN': """
Vấn đề
======
* Vấn đề xảy ra khi khách hàng thanh toán hoá đơn bằng loại tiền tệ mà Paypal không hỗ trợ do Paypal chỉ hỗ trợ một số loại tiền tệ nhất định
* Danh sách các loại tiền tệ mà Paypal hỗ trợ:  https://developer.paypal.com/docs/api/reference/currency-codes/

Mô tả
=====
* Khi khách hàng tiến hành thanh toán bằng một loại tiền tệ mà Paypal không hỗ trợ, mô-đun này sẽ quy đổi lượng tiền thanh toán này thành lượng tiền tệ mà Paypal hỗ trợ trước khi gửi dữ liệu thanh toán cho Paypal.
* Trong quá trình thanh toán và thông báo thanh toán, mô-đun này đảm bảo rằng lượng tiền tệ được quy đổi bằng với lượng tiền tệ ban đầu.
* Trong quá trình quy đổi, sự khác biệt về tỷ giá sẽ được mã hoá vào sổ nhật ký tỷ giá chuyển đổi.

Ví dụ
-----
* Giả định rằng

   * Đơn vị tiền tệ của công ty là VND (Việt Nam Đồng đ), đây là tiền tệ không được Paypal hỗ trợ.
   * Hoá đơn INV/2019/0001 là 2,000,010đ VND
   * Paypal được cấu hình USD là tiền tệ mặc định để chuyển đổi trong trường hợp này.
   * Tỷ giá chuyển đổi giữa VND/USD là 23,100

* Quá trình thanh toán

   * Chuyển đổi VND sang USD: 2,000,010  / 23,100 = 86.580519481, và được làm tròn thành 86.58.
   * Yêu cầu Paypal xử lý thanh toán với $86.58.
   * Sau khi xử lý, Paypal thông báo cho Odoo việc xử lý thành công khoản thanh toán $86.58.
   * Odoo xác minh khoản thanh toán này, tạo khoản thanh toán là $86.58 và vào sổ với giá trị $86.58 * 23,100 = 1,999,998đ
   * Trong quá trình chuyển đổi, phần giá trị chênh lệch 12đ sẽ được mã hoá vào phần chênh lệch chuyển đổi tỷ giá. Hoá đơn tương ứng sẽ được chuyển thành đã thanh toán.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['payment_paypal', 'to_currency_conversion_diff'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
