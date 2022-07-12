from odoo import fields
from odoo.tests import SavepointCase

class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        # Create a users
        cls.repair_manager = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Repair Manager',
            'login': 'manager',
            'email': 'manager@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_repair_access_group.group_repair_manager').id])]
        })

        cls.partner = cls.env.ref('base.res_partner_address_1')

        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.precision = cls.env['decimal.precision'].precision_get('Product Unit of Measure')

        cls.repair_location = cls.env['stock.location'].create({
            'name': 'Repair Location Test',
            'usage': 'internal',
            'location_id': cls.stock_location.id,
        })
        cls.warehouse_location = cls.env['stock.location'].create({
            'name': 'Warehouse Location Test',
            'usage': 'internal',
            'location_id': cls.stock_location.id,
        })
        cls.warehouse_location_shelf1 = cls.env['stock.location'].create({
            'name': 'Warehouse Location Shelf 1 Test',
            'usage': 'internal',
            'location_id': cls.warehouse_location.id,
        })
        cls.warehouse_location_shelf2 = cls.env['stock.location'].create({
            'name': 'Warehouse Location Shelf 2 Test',
            'usage': 'internal',
            'location_id': cls.warehouse_location.id,
        })

        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.uom_dozen = cls.env.ref('uom.product_uom_dozen')

        # Create products to repair
        cls.product_to_repair_consu = cls.env['product.product'].create({
            'name': 'Product To Repair Consumable',
            'type': 'consu',
            'default_code': 'CONSU001'
        })

        cls.product_to_repair = cls.env['product.product'].create({
            'name': 'Product To Repair',
            'type': 'product',
            'default_code': 'PRODUCT001'
        })

        cls.product_to_repair_serial = cls.env['product.product'].create({
            'name': 'Product To Repair Serial',
            'type': 'product',
            'tracking': 'serial',
            'default_code': 'SERIAL001'
        })

        cls.product_to_repair_lot = cls.env['product.product'].create({
            'name': 'Product To Repair Lot',
            'type': 'product',
            'tracking': 'lot',
            'default_code': 'LOT001'
        })
        cls.product_part_serial = cls.env['product.product'].create({
            'name': 'Product Part Serial',
            'type': 'product',
            'tracking': 'serial',
            'default_code': 'PARTSERIAL001'
        })
        cls.product_part_lot = cls.env['product.product'].create({
            'name': 'Product Part Lot',
            'type': 'product',
            'tracking': 'lot',
            'default_code': 'PARTLOT001'
        })
        cls.product_part_consu = cls.env['product.product'].create({
            'name': 'Product Part Consumable',
            'type': 'consu',
            'default_code': 'PARTCONSU001'
        })
        cls.product_part_product = cls.env['product.product'].create({
            'name': 'Product Part Product',
            'type': 'product',
            'default_code': 'PARTPRODUCT001'
        })
        cls.product_part_remove = cls.env['product.product'].create({
            'name': 'Product Part Remove',
            'type': 'product',
            'default_code': 'PARTREMOVE001'
        })
        cls.product_part_product_enough = cls.env['product.product'].create({
            'name': 'Product Part Product Enough',
            'type': 'product',
            'default_code': 'PARTPRODUCTENOUGH001'
        })
        cls.product_part_serial_not_enough = cls.env['product.product'].create({
            'name': 'Product Part Serial Not Enough',
            'type': 'product',
            'default_code': 'PARTSERIALNOTENOUGH001'
        })

        # Create lots of repair products
        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': cls.product_to_repair_serial.id,
            'company_id': cls.env.company.id,
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'name': 'lot2',
            'product_id': cls.product_to_repair_lot.id,
            'company_id': cls.env.company.id,
        })
        cls.lot3 = cls.env['stock.production.lot'].create({
            'name': 'lot3',
            'product_id': cls.product_to_repair_serial.id,
            'company_id': cls.env.company.id,
        })
        cls.lot4 = cls.env['stock.production.lot'].create({
            'name': 'lot4',
            'product_id': cls.product_to_repair_lot.id,
            'company_id': cls.env.company.id,
        })
        cls.lot5 = cls.env['stock.production.lot'].create({
            'name': 'lot5',
            'product_id': cls.product_part_serial.id,
            'company_id': cls.env.company.id,
        })
        cls.lot6 = cls.env['stock.production.lot'].create({
            'name': 'lot6',
            'product_id': cls.product_part_lot.id,
            'company_id': cls.env.company.id,
        })
        cls.lot7 = cls.env['stock.production.lot'].create({
            'name': 'lot7',
            'product_id': cls.product_part_serial_not_enough.id,
            'company_id': cls.env.company.id,
        })
        cls.lot8 = cls.env['stock.production.lot'].create({
            'name': 'lot8',
            'product_id': cls.product_part_serial_not_enough.id,
            'company_id': cls.env.company.id,
        })

        # Create repair order
        cls.repair1 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair_serial.id,
            'product_uom': cls.uom_unit.id,
            'product_qty': 1.0,
            'lot_id': cls.lot1.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': cls.stock_location.id,
        })
        cls.repair2 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair_lot.id,
            'product_qty': 2.0,
            'product_uom': cls.uom_unit.id,
            'lot_id': cls.lot2.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': cls.stock_location.id,
        })

        cls.repair_with_supply = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair.id,
            'product_qty': 2.0,
            'product_uom': cls.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': cls.repair_location.id,
            'partner_id': cls.partner.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': cls.product_part_product.id,
                    'product_uom_qty': 3.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 100,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_product.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Lot',
                    'type': 'add',
                    'product_id': cls.product_part_lot.id,
                    'lot_id': cls.lot6.id,
                    'product_uom_qty': 2.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_lot.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Serial',
                    'type': 'add',
                    'product_id': cls.product_part_serial.id,
                    'lot_id': cls.lot5.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_serial.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Remove',
                    'type': 'remove',
                    'product_id': cls.product_part_remove.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                    'location_id': cls.product_part_remove.property_stock_production.id,
                    'location_dest_id': cls.env['stock.location'].search([('scrap_location', '=', True), ('company_id', '=', cls.env.company.id)], limit=1).id,
                })
            ]
        })

        cls.repair_with_supply2 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair.id,
            'product_qty': 1.0,
            'product_uom': cls.uom_dozen.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': cls.repair_location.id,
            'partner_id': cls.partner.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': cls.product_part_product.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_dozen.id,
                    'price_unit': 100,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_product.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Lot',
                    'type': 'add',
                    'product_id': cls.product_part_lot.id,
                    'lot_id': cls.lot6.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_dozen.id,
                    'price_unit': 150,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_lot.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Serial',
                    'type': 'add',
                    'product_id': cls.product_part_serial.id,
                    'lot_id': cls.lot5.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_serial.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Remove',
                    'type': 'remove',
                    'product_id': cls.product_part_remove.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                    'location_id': cls.product_part_remove.property_stock_production.id,
                    'location_dest_id': cls.env['stock.location'].search([('scrap_location', '=', True), ('company_id', '=', cls.env.company.id)], limit=1).id,
                })
            ]
        })

        cls.repair_with_supply3 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair.id,
            'product_qty': 1.0,
            'product_uom': cls.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': cls.repair_location.id,
            'partner_id': cls.partner.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': cls.product_part_serial_not_enough.id,
                    'lot_id': cls.lot7.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 100,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_product.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Lot',
                    'type': 'add',
                    'product_id': cls.product_part_serial_not_enough.id,
                    'lot_id': cls.lot8.id,
                    'product_uom_qty': 1.0,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 100,
                    'src_location_id': cls.warehouse_location.id,
                    'location_id': cls.repair_location.id,
                    'location_dest_id': cls.product_part_lot.property_stock_production.id,
                })
            ]
        })

        cls.env['stock.quant']._update_available_quantity(cls.product_to_repair_serial, cls.repair_location, 1, lot_id=cls.lot3)
        cls.env['stock.quant']._update_available_quantity(cls.product_to_repair_lot, cls.repair_location, 2, lot_id=cls.lot4)
        cls.env['stock.quant']._update_available_quantity(cls.product_part_serial, cls.warehouse_location, 1, lot_id=cls.lot5)
        cls.env['stock.quant']._update_available_quantity(cls.product_part_lot, cls.warehouse_location, 2, lot_id=cls.lot6)
        cls.env['stock.quant']._update_available_quantity(cls.product_part_product, cls.warehouse_location, 3)
        cls.env['stock.quant']._update_available_quantity(cls.product_part_product_enough, cls.repair_location, 2)
        cls.env['stock.quant']._update_available_quantity(cls.product_to_repair, cls.warehouse_location_shelf1, 2)
        cls.env['stock.quant']._update_available_quantity(cls.product_to_repair, cls.warehouse_location_shelf2, 1)
