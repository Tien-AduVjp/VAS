from odoo.tests.common import tagged
from odoo.exceptions import UserError
from odoo.addons.to_quality.tests.common import Common


@tagged('-at_install', 'post_install')
class QualityStock(Common):

    def setUp(self):
        super(QualityStock, self).setUp()

        self.env.ref('product.product_product_27').tracking = 'none'
        self.picking = self.env['stock.picking'].with_context(tracking_disable=True).create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_company').id,
            'location_dest_id': self.env.ref('stock.stock_location_company').id,
            'move_lines': [(0, 0, {
                'name': self.env.ref('product.product_product_27').name,
                'product_id': self.env.ref('product.product_product_27').id,
                'product_uom_qty': 10,
                'location_id': self.env.ref('stock.stock_location_company').id,
                'location_dest_id': self.env.ref('stock.stock_location_company').id,
                'product_uom': self.env.ref('uom.product_uom_unit').id,
            })]
        })
        self.picking.action_confirm()

    def test_01_check_auto_create_quality_check(self):
        """
        Case 1: Tự động tạo QLC khi đánh dấu cần làm với dịch chuyển kho
        """
        check = self.env['quality.check'].search([('picking_id', '=', self.picking.id)], limit=1)
        self.assertEqual(len(check), 1)
        self.assertEqual(check.quality_state, 'none')

    def test_11_check_cancel_picking(self):
        """
        Case 2: Hủy dịch chuyển kho thì tự động xóa QLC tương ứng ở trạng thái cần làm
        """
        self.picking.action_cancel()
        check = self.env['quality.check'].search([('picking_id', '=', self.picking.id)], limit=1)
        self.assertEqual(len(check), 0)

    def test_12_check_cancel_picking(self):
        """
        Case 3: Hủy dịch chuyển kho thì không xóa QLC tương ứng ở trạng thái khác cần làm
        """
        check = self.env['quality.check'].search([('picking_id', '=', self.picking.id)], limit=1)
        check.do_pass()
        self.picking.action_cancel()
        check_1 = self.env['quality.check'].search([('picking_id', '=', self.picking.id)], limit=1)
        self.assertEqual(len(check_1), 1)

    def test_21_check_done_picking(self):
        """
        Case 4: Xác nhận dịch chuyển không bị chặn khi có QLC thất bại
        """
        check = self.env['quality.check'].search([('picking_id', '=', self.picking.id)], limit=1)
        check.do_fail()
        self.picking.move_ids_without_package.write({
            'quantity_done': 10
        })
        self.picking.button_validate()
        self.assertEqual(self.picking.state, 'done')

    def test_22_check_done_picking(self):
        """
        Case 5: Xác nhận dịch chuyển bị chặn khi có QLC thất bại
        """
        point = self.env.ref('to_quality_stock.quality_point1')
        point.write({
            'no_proceed_if_failed': True
        }) 
        check = self.env['quality.check'].search([('picking_id', '=', self.picking.id)], limit=1)
        check.do_fail()
        self.picking.move_ids_without_package.write({
            'quantity_done': 10
        })
        with self.assertRaises(UserError):
            self.picking.button_validate()

    def test_23_check_done_picking(self):
        """
        Case 6: Xác nhận dịch chuyển bị chặn khi có QLC cần làm
        """
        self.picking.move_ids_without_package.write({
            'quantity_done': 10
        })
        with self.assertRaises(UserError):
            self.picking.button_validate()
