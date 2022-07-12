from odoo.tests.common import SavepointCase, tagged, Form
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestPriceLock(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPriceLock, cls).setUpClass()
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.order = cls.env.ref('sale.sale_order_1')
        cls.sale_user_group = cls.env.ref('sales_team.group_sale_salesman')
        cls.user_demo.groups_id = [(4, cls.env.ref('sales_team.group_sale_salesman').id)]
        cls.public_pricelist = cls.env.ref('product.list0')
        cls.product_tmp_1 = cls.env.ref('product.product_delivery_01_product_template')
        cls.pricelist_item_data = {'product_tmpl_id': cls.product_tmp_1.id, 'fixed_price': 109}
        cls.uom_dozen = cls.env.ref('uom.product_uom_dozen')
        cls.env.company.write({'lock_sales_prices': True})

    def test_change_price_unit(self):
        """ User user does not belong to Sale Price Modifying Group
            Do not allow to change price unit
        """
        self.assertNotIn(self.env.company.sales_price_modifying_group_id, self.user_demo.groups_id)
        with self.assertRaises(UserError):
            self.order.with_user(self.user_demo).order_line[:1].write({'price_unit': 3000})

    def test_change_uom(self):
        """ User does not belong to Sale Price Modifying Group => Change UoM
            Expected result: price unit is recalculated according to the new uom
        """
        self.assertNotIn(self.env.company.sales_price_modifying_group_id, self.user_demo.groups_id)
        form = Form(self.order.with_user(self.user_demo))
        with form.order_line.edit(0) as order_line:
            order_line.product_uom = self.uom_dozen
        form.save()

    def test_change_uom_and_price(self):
        """
        Case: Người dùng không có quyền thay đổi giá bán, Kiểm tra thay đổi đơn vị và giá bán
        - Input: Thay đổi đơn vị tính và thay đổi giá bán khác với giá bán quy đổi tương ứng
        - Output: Xảy ra ngoại lệ
        """
        self.assertNotIn(self.env.company.sales_price_modifying_group_id, self.user_demo.groups_id)
        with self.assertRaises(UserError):
            self.order.with_user(self.user_demo).order_line[:1].write({
                'product_uom': self.uom_dozen.id,
                'price_unit': 1
            })

    def test_change_price_unit_2(self):
        """
        Case: Thay đổi giá sản phẩm 1 trên báo giá khi thay đổi lại giá trong bảng giá
        Input:
            - Người dùng không thuộc nhóm sửa đổi giá bán
            - Thiết lập hoặc thay đổi giá sản phẩm 1 trên bảng giá là 109
        Output: Nhân viên sửa báo giá sản phẩm 1 là 109 thành công, sửa giá khác không thành công
        """
        self.public_pricelist.write({'item_ids': [(0, 0, self.pricelist_item_data)]})
        order_line = self.order.order_line.filtered(lambda l: l.product_id.product_tmpl_id == self.product_tmp_1)[:1]
        #price change to 109
        order_line.with_user(self.user_demo).write({'price_unit': 109})
        #other price change 109
        with self.assertRaises(UserError):
            order_line.with_user(self.user_demo).write({'price_unit': 100})

    def test_change_price_unit_3(self):
        """
        Case: Thay đổi giá sản phẩm trên báo giá, người dùng thuộc nhóm sửa đổi giá bán
        Input:
            - Người dùng thuộc nhóm sửa đổi giá bán
            - Thay đổi giá bán sản phẩm trên báo giá
        Output: Sửa thành công
        """
        self.env.company.write({'sales_price_modifying_group_id': self.sale_user_group.id})
        self.assertIn(self.env.company.sales_price_modifying_group_id, self.user_demo.groups_id)
        self.order.with_user(self.user_demo).order_line[:1].write({'price_unit': 3000})
