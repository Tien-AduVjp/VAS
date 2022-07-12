from odoo.tests.common import SavepointCase, tagged, Form


@tagged('-at_install', 'post_install')
class TestStockProductionLot(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockProductionLot, cls).setUpClass()

        # Product
        # product tracking Lots/Serial
        product_1_form = Form(cls.env['product.product'])
        product_1_form.name = 'Product 2'
        product_1_form.type = 'product'
        product_1_form.tracking = 'serial'
        cls.product_1 = product_1_form.save()

        # Lot
        cls.lot_1 = cls.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_qty': 1,
            'product_id': cls.product_1.id,
            'company_id': cls.env.company.id,
        })

        #Supplier
        cls.supplier_1 = cls.env.ref('base.res_partner_1')
        #Customer
        cls.customer_1 = cls.env.ref('base.res_partner_address_15')

        #Location
        cls.partner_location = cls.env.ref('stock.stock_location_customers')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.company_location = cls.env.ref('stock.stock_location_stock')

        #Stock Picking Type
        cls.operation_type_receipt = cls.env.ref('stock.picking_type_in')
        cls.operation_type_delivery = cls.env.ref('stock.picking_type_out')

        #Picking
        # Receiving from supplier warehouse to internal warehouse
        cls.picking_1 = cls.env['stock.picking'].create({
            'partner_id': cls.supplier_1.id,
            'picking_type_id': cls.operation_type_receipt.id,
            'location_id' : cls.supplier_location.id,
            'location_dest_id': cls.company_location.id,
        })
        # Move from internal warehouse to customer warehouse
        cls.picking_2 = cls.env['stock.picking'].create({
            'partner_id': cls.customer_1.id,
            'picking_type_id': cls.operation_type_delivery.id,
            'location_id' : cls.company_location.id,
            'location_dest_id': cls.partner_location.id,
        })
        # Move from supplier warehouse to customer warehouse
        cls.picking_3 = cls.env['stock.picking'].create({
            'partner_id': cls.customer_1.id,
            'picking_type_id': cls.operation_type_delivery.id,
            'location_id' : cls.supplier_location.id,
            'location_dest_id': cls.partner_location.id,
        })

    def test_receive_from_supplier_to_internal_01(self):
        #Case 1: Nhận hàng từ kho NCC đến kho nội bộ với sản phẩm lưu kho và theo dõi bởi số Serial, có thông tin NCC
        # -> Lot/serial sản phẩm có thông tin NCC
        stock_move_line_data = {
            'product_id': self.product_1.id,
            'qty_done': 1,
            'product_uom_id': self.product_1.uom_id.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.company_location.id,
            'lot_name': 'lot_product_01',
            'picking_id': self.picking_1.id,

        }
        stock_move_line = self.env['stock.move.line'].create(stock_move_line_data)
        self.picking_1.button_validate()
        lot_production = self.picking_1.move_line_ids.lot_id
        self.assertIn(self.supplier_1, lot_production.supplier_id)

    def test_receive_from_supplier_to_internal_02(self):
        #Case 2: Nhận hàng từ kho NCC đến kho nội bộ không chọn thông tin nhà cung cấp
        # -> Trên lot/serial không có thông tin NCC
        stock_move_line_data = {
            'product_id': self.product_1.id,
            'qty_done': 1,
            'product_uom_id': self.product_1.uom_id.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.company_location.id,
            'lot_name': 'lot_product_01',
            'picking_id': self.picking_1.id,

        }
        stock_move_line = self.env['stock.move.line'].create(stock_move_line_data)
        self.picking_1.write({'partner_id': False})
        self.picking_1.button_validate()
        lot_production = self.picking_1.move_line_ids.lot_id
        self.assertFalse(lot_production.supplier_id)

    def test_delivery_from_internal_to_customer_01(self):
        #Case 1: Giao hàng từ kho nội bộ đến KH với sản phẩm lưu kho theo dõi bởi số Lot/Serial, có thông tin KH
        # -> Lot/serial tương ứng sản phẩm cập nhật thông tin KH
        stock_move_line_data = {
            'product_id': self.product_1.id,
            'qty_done': 1,
            'product_uom_id': self.product_1.uom_id.id,
            'location_id': self.company_location.id,
            'location_dest_id': self.partner_location.id,
            'lot_id': self.lot_1.id,
            'picking_id': self.picking_2.id,

        }
        stock_move_line = self.env['stock.move.line'].create(stock_move_line_data)
        self.picking_2.button_validate()
        self.assertEqual(self.lot_1.customer_id, self.picking_2.partner_id)

        #Test: Khách hàng trả lại sản phẩm
        # -> Thông tin khách hàng trên số Lô/seri bị xoá
        stock_return_picking_form = Form(self.env['stock.return.picking'])
        stock_return_picking_form.picking_id = self.picking_2
        stock_return_picking = stock_return_picking_form.save()
        res_stock_return_picking = stock_return_picking.create_returns()
        stock_picking_return = self.env['stock.picking'].browse([res_stock_return_picking.get('res_id')])
        stock_picking_return.move_line_ids.write({
            'lot_id': self.lot_1
        })
        stock_picking_return.button_validate()
        self.assertFalse(self.lot_1.customer_id)
        self.assertFalse(self.lot_1.country_state_id)

    def test_delivery_from_internal_to_customer_02(self):
        #Case 2: Giao hàng từ kho nội bộ đến KH với sản phẩm lưu kho theo dõi bởi số Lot/Serial, không có thông tin KH
        # -> Lot/serial tương ứng sản phẩm không cập nhật thông tin KH
        stock_move_line_data = {
            'product_id': self.product_1.id,
            'qty_done': 1,
            'product_uom_id': self.product_1.uom_id.id,
            'location_id': self.company_location.id,
            'location_dest_id': self.partner_location.id,
            'lot_id': self.lot_1.id,
            'picking_id': self.picking_2.id,

        }
        stock_move_line = self.env['stock.move.line'].create(stock_move_line_data)
        self.picking_2.write({'partner_id': False})
        self.picking_2.button_validate()
        self.assertFalse(self.lot_1.customer_id)

    def test_delivery_from_supplier_to_customer_01(self):
        #Case 1: Giao hàng từ kho NCC đến KH với sản phẩm lưu kho theo dõi bởi số Lot/Serial, có thông tin KH/NCC
        # -> Lot/serial tương ứng sản phẩm cập nhật thông tin KH/NCC
        stock_move_line_data = {
            'product_id': self.product_1.id,
            'qty_done': 1,
            'product_uom_id': self.product_1.uom_id.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.partner_location.id,
            'lot_id': self.lot_1.id,
            'picking_id': self.picking_3.id,

        }
        stock_move_line = self.env['stock.move.line'].create(stock_move_line_data)
        self.picking_3.button_validate()
        self.assertFalse(self.lot_1.customer_id)
        self.assertEqual(self.lot_1.supplier_id, self.picking_3.partner_id)

    def test_delivery_from_supplier_to_customer_02(self):
        #Case 2: Giao hàng từ kho NCC đến KH với sản phẩm lưu kho theo dõi bởi số Lot/Serial, không có thông tin KH/NCC
        # -> Lot/serial tương ứng sản phẩm không cập nhật thông tin KH/NCC
        stock_move_line_data = {
            'product_id': self.product_1.id,
            'qty_done': 1,
            'product_uom_id': self.product_1.uom_id.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.partner_location.id,
            'lot_id': self.lot_1.id,
            'picking_id': self.picking_3.id,

        }
        stock_move_line = self.env['stock.move.line'].create(stock_move_line_data)
        self.picking_3.write({'partner_id': False})
        self.picking_3.button_validate()
        self.assertFalse(self.lot_1.customer_id)
        self.assertFalse(self.lot_1.supplier_id)

    def test_stock_production_lot_change_customer(self):
        #Input: Thay đổi thông tin khách hàng của số lô/seri
        #Output: Tỉnh/thành phục vụ của số lô/seri được cập nhật theo địa chỉ của khách hàng
        lot = Form(self.lot_1)
        lot.customer_id = self.customer_1
        self.assertEqual(lot.country_state_id.id, self.customer_1.state_id.id)
