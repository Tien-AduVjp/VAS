{
    'name': "Remove Only Reference From One2many",
    'name_vi_VN': "Chỉ Loại Bỏ Liên Kết One2many",

    'summary': """
        Only remove the One2many field association without removing it from the database
    """,

    'summary_vi_VN': """
        Chỉ xoá liên kết trường One2many mà không xoá nó khỏi cơ sở dữ liệu 
    """,

    'description': """
What it does
============

Problem
-------
By default, when you delete the data of the one2many field on the view and then save it, the data is deleted from the database, this will not be true if that data is needed for many other models.

Solution
--------
This module is the base module to prevent deleting data from the database if desired.

How to use
----------
Use ```effect``` attribute add one2many field on view (\*.xml). For example

.. code-block:: xml

  <field name="field_one2many" effect="{'remove_only_reference_from_one2many':true}"></field>

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

Vấn đề
------
Mặc định, khi thực hiện xoá dữ liệu từ trường One2many trên giao diện sau đó ấn lưu lại thì dữ liệu đó đã bị xoá khỏi cơ sở dữ liệu, điều này sẽ không đúng nếu dữ liệu đó cần dùng cho nhiều model khác.

Giải pháp
---------
Đây là mô-đun cơ sở để ngăn việc xoá dữ liệu từ trường One2many khỏi cơ sở dữ liệu nếu muốn.

Cách sử dụng
------------
Sử dụng thuộc tính ```effect``` thêm vào trường One2many trên chế độ xem (\*.xml):

.. code-block:: xml

    Ví dụ: <field name="field_one2many" effect="{'remove_only_reference_from_one2many':true}"></field>

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
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
        'views/assets.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
