from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.to_product_return_reason.tests.common import ProductReturnReasonCommon


@tagged('post_install', '-at_install')
class TestProductReturnReasonStock(ProductReturnReasonCommon):

    @classmethod
    def setUpClass(cls):
        super(TestProductReturnReasonStock, cls).setUpClass()
        cls.stock_picking = cls.env.ref('stock.incomming_chicago_warehouse1')

    def test_01_stock_return_picking(self):
        stock_return_picking = self.env['stock.return.picking'].create({
            'picking_id': self.stock_picking.id,
            'location_id': self.stock_picking.location_id.id,
            'product_return_moves': [(0, 0, {
                'product_id': self.stock_picking.move_lines[0].move_line_ids[0].product_id.id,
                'quantity': 10,
                'move_id': self.stock_picking.move_lines[0].id,
                'return_reason_id':self.reason_1.id
            })]
        })
        result = stock_return_picking.create_returns()
        stock_picking_return_id = result['res_id']
        stock_picking_return = self.env['stock.picking'].browse(stock_picking_return_id)
        self.assertEqual(stock_picking_return.return_reason_ids[0].id, self.reason_1.id,
                         "to_product_return_reason_stock: error return reason")
        stock_move = stock_picking_return.move_lines[0]
        self.assertEqual(stock_move.return_reason_id.id, self.reason_1.id,
                         "to_product_return_reason_stock: error return reason")

    def test_02_return_reason_required(self):
        return_picking_type_id = self.stock_picking.picking_type_id.return_picking_type_id
        return_picking_type_id.return_reason_required = True
        stock_return_picking = self.env['stock.return.picking'].create({
            'picking_id': self.stock_picking.id,
            'location_id': self.stock_picking.location_id.id,
            'product_return_moves': [(0, 0, {
                'product_id': self.stock_picking.move_lines[0].move_line_ids[0].product_id.id,
                'quantity': 10,
                'move_id': self.stock_picking.move_lines[0].id,
            })]
        })
        with self.assertRaises(UserError):
            stock_return_picking.create_returns()
