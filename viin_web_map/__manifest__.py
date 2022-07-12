{
    'name': "Viin Map View",
    'name_vi_VN': "Viin Giao diện bản đồ",
    'summary': "Defines the viin_map view for Odoo",
    'summary_vi_VN': "Định nghĩa giao diện viin_map cho Odoo",
    'description': """
What it does
============
Base module for others to extend to present model records on a map (e.g. contacts map, employee map, opportunity map, etc).
Depending on map provider is selected, either or more of the following features are supported

1. Map Markers
2. Map Routing (get directions)

Examples
========

#. Present contacts on map

  .. code-block:: xml

    <record id="res_partner_view_map" model="ir.ui.view">
        <field name="name">res.partner.view.map</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <viin_map res_partner="id">
                <marker-popup>
                    <field name="name" string="Name "/>
                    <field name="mapping_address" string="Address "/>
                </marker-popup>
            </viin_map>
        </field>
    </record>

#. Present employees on map

  .. code-block:: xml

    <record id="hr_employee_view_viin_map" model="ir.ui.view">
        <field name="name">hr.employee.view.viin_map</field>
        <field name="model">hr.employee</field>
        <field name="arch" type="xml">
            <viin_map res_partner="address_home_id">
                <marker-popup>
                    <field name="name" string="Name " />
                    <field name="address_home_id" string="Address " />
                </marker-popup>
            </viin_map>
        </field>
    </record>

Editions Supported
==================
1. Community Edition

     """,
    'description_vi_VN': """
Mô tả
=====
Đây là mô-đun cơ sở cho các mô-đun khác mở rộng để hiển thị hình ảnh bản đồ cho các thông tin liên quan đến địa chỉ (ví dụ: Bản đồ theo địa chỉ trên liên hệ, bản đồ theo địa chỉ nhân viên, v.v.).
Tùy thuộc vào loại bản đồ được lựa chọn, mô-đun này sẽ hỗ trợ một hoặc các tính năng sau:

1. Đánh dấu địa chỉ trên bản đồ
2. Định tuyến trên bản đồ (chỉ đường)

Ví dụ
=====

#. Hiển thị danh bạ trên bản đồ

  .. code-block:: xml

    <record id="res_partner_view_map" model="ir.ui.view">
        <field name="name">res.partner.view.map</field>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
            <viin_map res_partner="id">
                <marker-popup>
                    <field name="name" string="Name "/>
                    <field name="mapping_address" string="Address "/>
                </marker-popup>
            </viin_map>
        </field>
    </record>

#. Hiển thị nhân viên trên bản đồ

  .. code-block:: xml

    <record id="hr_employee_view_viin_map" model="ir.ui.view">
        <field name="name">hr.employee.view.viin_map</field>
        <field name="model">hr.employee</field>
        <field name="arch" type="xml">
            <viin_map res_partner="address_home_id">
                <marker-popup>
                    <field name="name" string="Name " />
                    <field name="address_home_id" string="Address " />
                </marker-popup>
            </viin_map>
        </field>
    </record>

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

  """,
    'category': 'Hidden',
    'version': '1.0',
    'author': 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    # although the base_geolocalize depends on base_setup, its is required to have base_setup in the depends list
    # to ensure auto_install works
    'depends': ['web', 'base_setup', 'base_geolocalize'],
    'data': [
        'data/geoprovider_data.xml',
        'data/scheduler_data.xml',
        'views/assets.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
    ],
    'qweb': [
        "static/src/xml/templates.xml"
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': ['web', 'base_setup'],
    'price': 999.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
