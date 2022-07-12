{
    'name': "Viin Web Dashboard",
    'name_vi_VN': "Viin Web Dashboard",
    'category': 'Hidden',
    'version': '1.0',
    'author': 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'description':
        """

What it does
============
This module defines the Viin Dashboard view, a new type of reporting view. This view can embed different graph views and displays aggregate values.

Key Features
------------
* Allow to display one or more selected chart views on the App Dashboard
* Available chart views: line chart, bar chart, pie chart, stacked chart, pivot table
* Additional chart views when integrating viin_web_cohort module: cohort view

Example
-------
Embed graph and pivot and viin_cohort into sales report dashboard

.. code-block:: xml

  <record id="sale_report_view_viin_dashboard" model="ir.ui.view">
        <field name="name">sale.report.view.viin_dashboard</field>
        <field name="model">sale.report</field>
        <field name="mode">primary</field>
        <field name="arch" type="xml">
            <viin_dashboard>
                <view type="graph" ref="sale.view_order_product_graph" />
                <group>
                    <group>
                        <aggregate name="price_subtotal_confirmed_orders"
                            string="Total Sales" field="price_total"
                            help="Total, Tax Included" widget="monetary" />
                        <aggregate name="price_subtotal_all_orders"
                            string="Untaxed Total" field="price_subtotal" widget="monetary" />
                        <aggregate name="order_id_confirmed_orders"
                            field="order_id" string="Orders" />
                        <formula name="total" string="Average Order"
                            value="record.price_subtotal_confirmed_orders / record.order_id_confirmed_orders"
                            widget="monetary" />
                        <aggregate name="customers" string="# Customers"
                            field="partner_id" />
                        <aggregate name="lines" string="# Lines" field="nbr" />
                    </group>
                    <group col="1">
                        <widget name="pie_chart" title="Sales Teams"
                            attrs="{'groupby': 'team_id'}" />
                    </group>
                </group>
                <view type="pivot" ref="viin_sale.sale_report_view_pivot" />
                <view type="viin_cohort" ref="viin_sale.sale_report_view_viin_cohort"/>
            </viin_dashboard>
        </field>
    </record>

Editions Supported
======================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Mô tả
=====
Mô-đun xác định chế độ xem báo cáo ở ngay trang Tổng quan của bất kỳ ứng dụng nào, cho phép kết hợp nhiều biểu đồ và hiển thị dữ liệu một cách tổng hợp, xuyên suốt.

Tính năng nổi bật
-----------------
* Cho phép hiển thị một hoặc nhiều kiểu biểu đồ tùy chọn trên trang Tổng quan của ứng dụng
* Các loại biểu đồ có sẵn: biểu đồ đường, biểu đồ cột, biểu đồ tròn, biểu đồ xếp chồng, bảng tổng hợp (pivot)
* Các loại biểu đồ mở rộng khi tích hợp thêm module viin_web_cohort: bảng tổ hợp (cohort)

Ví dụ
-----
Kết hợp biểu đồ, bảng tổng hợp pivot và viin_cohort trong báo cáo Tổng quan bán hàng

.. code-block:: xml

  <record id="sale_report_view_viin_dashboard" model="ir.ui.view">
        <field name="name">sale.report.view.viin_dashboard</field>
        <field name="model">sale.report</field>
        <field name="mode">primary</field>
        <field name="arch" type="xml">
            <viin_dashboard>
                <view type="graph" ref="sale.view_order_product_graph" />
                <group>
                    <group>
                        <aggregate name="price_subtotal_confirmed_orders"
                            string="Total Sales" field="price_total"
                            help="Total, Tax Included" widget="monetary" />
                        <aggregate name="price_subtotal_all_orders"
                            string="Untaxed Total" field="price_subtotal" widget="monetary" />
                        <aggregate name="order_id_confirmed_orders"
                            field="order_id" string="Orders" />
                        <formula name="total" string="Average Order"
                            value="record.price_subtotal_confirmed_orders / record.order_id_confirmed_orders"
                            widget="monetary" />
                        <aggregate name="customers" string="# Customers"
                            field="partner_id" />
                        <aggregate name="lines" string="# Lines" field="nbr" />
                    </group>
                    <group col="1">
                        <widget name="pie_chart" title="Sales Teams"
                            attrs="{'groupby': 'team_id'}" />
                    </group>
                </group>
                <view type="pivot" ref="viin_sale.sale_report_view_pivot" />
                <view type="viin_cohort" ref="viin_sale.sale_report_view_viin_cohort"/>
            </viin_dashboard>
        </field>
    </record>

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'depends': ['web'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        "static/src/xml/viin_dashboard.xml",
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 999.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
