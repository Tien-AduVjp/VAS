{
    'name': "WMS Landed Cost Tuning",
    'name_vi_VN': "Tinh chỉnh Chi Phí Về Kho",

    'summary': """
Fix and Tune the Odoo core's Stock Landed Cost
""",
    'summary_vi_VN': """
Tinh chỉnh và xử lý các vấn đề của tính năng Chi phí về kho
""",

    'description': """
This module offer additional tunes for the Odoo core's Stock Landed Cost

Key Features
============

#. Fix currency rounding issue that causes losing landed cost in accounting when the currency
   rounding digits is less than the Product Price's precision digits

   * Assume:

     * We have 3 items for landed cost adjustment
     * Total landed cost to allocated for the whole 3 items is 100
     * The given currency's decimal places is 0 (e.g. VND has zero decimal place)

   * Without this module:

     * adjustment lines may look like

       * item 1: 33.34
       * item 2: 33.34
       * item 3: 33.32

     * and the account move will round them all to say 99 in total since the currency's decimal place is 0. Hence, we lost 1 in accounting

   * This module correct the above mentioned problem to make things done as below

     * adjustment lines will look like

       * item 1: 33
       * item 2: 33
       * item 3: 34

     * and the account move will round them all to say 100 in total. Nothing lost here

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Module này cung cấp các tinh chỉnh và xử lý các lỗi của Odoo liên quan đến Phí về kho

Tính năng chính
===============
#. Sửa lỗi liên quan đến mất giá trị ở kế toán do làm tròn tiền tệ

   * Giả sử:

     * Chúng ta có 3 hạng mục để phân bổ phí về kho
     * Tổng chi phí về kho cho cả 3 hạng mục là 100
     * Tiền tệ được cấu hình làm tròn về số nguyên, không có phần thập phân (vd VNĐ không có phần thập phân)

   * Khi không có module này:

     * Các dòng phân bổ chi phí về kho cho 3 hạng mục nói trên sẽ trông như sau

       * mục 1: 33.34
       * mục 2: 33.34
       * mục 3: 33.32

     * Khi bút toán kế toán được tạo, do tiền tệ không có phần thập phân nên các tổng các phát sinh kế toán chỉ còn lại 99. Chúng ta mất 1 đơn vị tiền tệ ở đây.

   * Module này sẽ xử lý vấn đề trên bằng cách làm tròn luôn ở chỗ phân bổ chi phí về kho.

     * các dòng phân bổ trông sẽ như sau

       * mục 1: 33
       * mục 2: 33
       * mục 3: 34

     * và vì thế, bút toán tạo ra sẽ mang giá trị đủ 100.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Warehouse',
    'version': '0.1',
    'depends': ['stock_landed_costs'],
    'data': [

    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
