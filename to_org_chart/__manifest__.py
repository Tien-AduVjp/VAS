# -*- coding: utf-8 -*-
{
    'name': "Org Chart",
    'name_vi_VN': "Biểu đồ tổ chức doanh nghiệp",

    'summary': """
Provide Organization Chart view to others to use
    """,

    'summary_vi_VN': """ 
Cung cấp giao diện Sơ đồ tổ chức cho các module khác tái sử dụng
    """,

    'description': """
Key features
============
* Provide Organization Chart view to other modules to use by defining additional `org` view (displaying data in the form of an organization chart) beside existing view modes such as 

   * `list view` (displays data as a list)
   * `kanban view` (displays data in tags)
   * `form view` (displays detailed data of a record, from which you can edit, select), etc in windows actions. 

* Here is an example of the `org` view in OKR application

  .. code-block:: xml

    <record id="okr_node_action" model="ir.actions.act_window">
        <field name="name">OKR Node</field>
        <field name="res_model">okr.node</field>
        <field name="type">ir.actions.act_window</field>
        <field name="view_mode">tree,form,org</field>
    </record>

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Cung cấp giao diện Sơ đồ tổ chức cho các mô-đun khác tái sử dụng, bằng cách bổ sung thêm chế độ xem `org` bên cạnh các chế độ xem đã có như 

   * `list view` (hiển thị dữ liệu theo dạng danh sách) 
   * `kanban view` (hiển thị dữ liệu theo dạng thẻ) 
   * `form view` (hiển thị dữ liệu chi tiết của một bản ghi, từ đó người dùng có thể chỉnh sửa), v.v.

* Ví dụ: giao diện Sơ đồ tổ chức trong ứng dụng OKR

  .. code-block:: xml

    <record id="okr_node_action" model="ir.actions.act_window">
        <field name="name">OKR Node</field>
        <field name="res_model">okr.node</field>
        <field name="type">ir.actions.act_window</field>
        <field name="view_mode">tree,form,org</field>
    </record>

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
    'category': 'Human Resources/OKR',
    'version': '0.1',
    'depends': ['web'],
    'data': [
        'views/assets.xml'
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 199.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
