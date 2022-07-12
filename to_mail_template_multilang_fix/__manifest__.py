{
    'name': "Mail Template Multilingual Fix",
    'name_vi_VN': 'Sửa lỗi đa ngôn ngữ cho mẫu email',
    'summary': """
Fix mail templates for multilingual""",

    'summary_vi_VN': """
Sửa lỗi đa ngôn ngữ cho một số mẫu email
    	""",

    'description': """
Problems
========
The following email templates come with a piece of code that does not support multi-languages

* mail_notification_light
* mail_notification_paynow

They come with the following code

.. code:: html

  <span style="font-size: 10px;">Your <t t-esc="model_description or 'document'"/></span>

It is obviously that they will always produce something like "Your document" no matter the language is. In some languages, the expected result will be "Document Your".

This module modifies the above mentioned code by removing the "Your " to say

.. code:: html

  <span style="font-size: 10px;"><t t-esc="model_description or 'document'"/></span>

It would be acceptable in all cases to just show something like "Document" instead of "Your document".

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Vấn đề
======
Các mẫu email dưới đây cung cấp một đoạn code mà không hỗ trợ đa ngôn ngữ như tiếng Việt chẳng hạn.

* mail_notification_light
* mail_notification_paynow

Các mẫu này chứa đoạn code sau
.. code:: html

  <span style="font-size: 10px;">Your <t t-esc="model_description or 'document'"/></span><br/>

Rõ ràng là đoạn code này không hỗ trợ đa ngôn ngữ vì nó luôn luôn tạo ra kết quả là "Your Document" hay khi dịch ra tiếng Việt sẽ là "Của bạn Tài liệu", trong khi kết quả mong đợi ở tiếng Việt phải là "Tài liệu của bạn".

Module này điều chỉnh lại 2 mẫu email nói trên bằng cách loại bỏ "Your " để thành

.. code:: html

  <span style="font-size: 10px;"><t t-esc="model_description or 'document'"/></span><br/>

Điều này là hoàn toàn chấp nhận được trong mọi trường hợp vì nó sẽ chỉ tạo ra đoạn văn bản "Tài liệu" thay vì "Của bạn Tài liệu"

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Discuss',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        'data/mail_data.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
