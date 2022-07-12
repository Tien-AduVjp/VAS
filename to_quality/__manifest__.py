{
    'name': 'Quality',
    'name_vi_VN': 'Quản lý Chất lượng',
    'summary': 'Quality Alerts and Control Points',
    'summary_vi_VN': 'Cảnh báo chất lượng và Tiêu chí kiểm soát chất lượng',

    'description': """
Key Features
============

* Define quality points
* Create and manage quality checks
* Quality alerts can be created independently or related to quality checks
* Define and manage Alert Actions (corrective actions, preventive actions) on each and every Quality Alert
* Possibility to add a measure to the quality check with a min/max tolerance
* Define your stages for the quality alerts
* Analyse Quality Action
* SPC reports

The Base
========

This application is the base for all kind of Quality Control features developments. It offers the following base models for other applications to extend

Modeling
--------

It offers the following base models for other applications to extend

1. Quality Point
2. Quality Check
3. Quality Alert
4. Quality Reason
5. Quality Tag
6. Quality Alert Action, that is the consolidation of

   * Quality Alert Prevention Action
   * Quality Alert Corrective Action

7. Other technical models

Base Reports and Analysis system
--------------------------------

1. Quality Alert Analysis
2. Statistical process control (aka Quality Check Analysis)
3. Alert Action Analysis

Editions Supported
==================

1. Community
2. Enterprise, with prior removal the of Enterprise Edition's Quality application

""",
    'description_vi_VN': """
Tính năng chính
===============

* Xác định các tiêu chí kiểm soát chất lượng
* Tạo và quản lý kiểm tra chất lượng
* Cảnh báo chất lượng có thể được tạo độc lập hoặc liên quan đến kiểm tra chất lượng
* Xác định và quản lý Hành động cảnh báo (hành động khắc phục, hành động phòng ngừa) trên mỗi và mọi Cảnh báo chất lượng
* Khả năng thêm đo lường vào kiểm tra chất lượng với dung sai tối thiểu/tối đa
* Xác định các giai đoạn của bạn cho các cảnh báo chất lượng
* Phân tích hành động chất lượng
* Báo cáo SPC

Cơ sở
=====

Ứng dụng này là cơ sở cho tất cả các loại phát triển tính năng Kiểm soát chất lượng. Cung cấp các mô hình cơ sở sau cho các ứng dụng khác để mở rộng

Mô hình
-------

Cung cấp các mô hình cơ sở sau cho các ứng dụng khác để mở rộng
1. Tiêu chí kiểm soát chất lượng
2. Kiểm tra chất lượng
3. Cảnh báo chất lượng
4. Lý do chất lượng
5. Thẻ chất lượng
6. Hành động cảnh báo chất lượng, đó là sự hợp nhất của

   * Hành động cảnh báo chất lượng
   * Hành động khắc phục cảnh báo chất lượng

7. Các mô hình kỹ thuật khác

Hệ thống phân tích và báo cáo cơ sở
-----------------------------------

1. Phân tích cảnh báo chất lượng
2. Kiểm soát quá trình thống kê (còn gọi là Phân tích kiểm tra chất lượng)
3. Phân tích hành động cảnh báo

Ấn bản được Hỗ trợ
==================

1. Ấn bản Community
2. Ấn bản Enterprise, nhưng phải gỡ ứng dụng Chất lượng của ấn bản Enterprise trước.

""",

    'old_technical_name': 'quality',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Operations/Quality Control',
    'version': '0.1.2',
    'sequence': 50,

    'depends': ['mail'],
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'data/quality_data.xml',
        'data/ir_sequence_data.xml',
        'views/root_menu.xml',
        'views/assets.xml',
        'views/quality_type_views.xml',
        'views/quality_tag_views.xml',
        'views/quality_alert_views.xml',
        'views/quality_check_views.xml',
        'views/quality_alert_team_views.xml',
        'views/quality_alert_stage_views.xml',
        'views/quality_point_views.xml',
        'views/quality_action_views.xml',
        'views/quality_alert_action_views.xml',
        'views/quality_alert_corrective_action_views.xml',
        'views/quality_alert_preventive_action_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 198.9,
    'subscription_price': 9.93,
    'currency': 'EUR',
    'license': 'OPL-1',
}
