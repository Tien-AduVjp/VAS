from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from odoo.addons.to_quality.tests.common import Common


@tagged('-at_install', 'post_install', 'access_rights')
class QualityStockAccessRight(Common):

    def test_01_check_quality_user(self):
        lot_product_cable_management = self.env.ref('stock.lot_product_cable_management').with_user(self.quality_user)
        # Quality User can see the stock production lot
        lot_product_cable_management.read()
        # Quality User can't create the stock production lot
        with self.assertRaises(AccessError):
            self.env['stock.production.lot'].with_user(self.quality_user).create({
                'name': 'LOT-0000001',
                'product_id': self.env.ref('stock.product_cable_management_box').id,
                'company_id': self.env.ref('base.main_company').id,
            })
        # Quality User can't edit the stock production lot
        with self.assertRaises(AccessError):
            lot_product_cable_management.write({
                'name': 'LOT-0000002',
            })
        # Quality User can't delete the stock production lot
        with self.assertRaises(AccessError):
            lot_product_cable_management.unlink()

        picking_type_in = self.env.ref('stock.picking_type_in').with_user(self.quality_user)
        # Quality User can see the stock picking type
        picking_type_in.read()
        # Quality User can't create the stock picking type
        with self.assertRaises(AccessError):
            self.env['stock.picking.type'].with_user(self.quality_user).create({
                'name': 'New Receipt 1',
                'sequence_code': 'IN',
                'code': 'incoming',
                'warehouse_id': self.env.ref('stock.warehouse0').id
            })
        # Quality User can't edit the stock picking type
        with self.assertRaises(AccessError):
            picking_type_in.write({
                'name': 'New Receipt 2',
            })
        # Quality User can't delete the stock picking type
        with self.assertRaises(AccessError):
            picking_type_in.unlink()

        incomming_shipment = self.env.ref('stock.outgoing_shipment_main_warehouse').with_user(self.quality_user)
        # Quality User can see the stock picking
        incomming_shipment.read()
        # Quality User can't create the stock picking
        with self.assertRaises(AccessError):
            self.env['stock.picking'].with_user(self.quality_user).with_context(tracking_disable=True).create({
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
        # Quality User can't edit the stock picking
        with self.assertRaises(AccessError):
            incomming_shipment.write({
                'partner_id': self.env.ref('base.res_partner_2').id,
            })
        # Quality User can't delete the stock picking
        with self.assertRaises(AccessError):
            incomming_shipment.unlink()

    def test_11_check_quality_manager(self):
        picking_type_in = self.env.ref('stock.picking_type_in').with_user(self.quality_manager)
        # Quality Manager can see the stock picking type
        picking_type_in.read()
        # Quality Manager can't create the stock picking type
        with self.assertRaises(AccessError):
            self.env['stock.picking.type'].with_user(self.quality_manager).create({
                'name': 'New Receipt 1',
                'sequence_code': 'IN',
                'code': 'incoming',
                'warehouse_id': self.env.ref('stock.warehouse0').id
            })
        # Quality Manager can edit the stock picking type
        picking_type_in.write({
            'name': 'New Receipt 2',
        })
        # Quality Manager can't delete the stock picking type
        with self.assertRaises(AccessError):
            picking_type_in.unlink()
