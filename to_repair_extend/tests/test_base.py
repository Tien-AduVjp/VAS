from odoo import fields
from odoo.tests import SavepointCase

class TestBase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        
        cls.company = cls.env['res.company'].create({'name': 'A company'})
        
        # Setup user
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        # Create a users
        cls.stock_user = Users.create({
            'name': 'Stock User',
            'login': 'user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('stock.group_stock_user').id])]
        })
        cls.stock_manager = Users.create({
            'name': 'Stock Manager',
            'login': 'manager',
            'email': 'manager@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('stock.group_stock_manager').id])]
        })
        
        cls.partner_a = cls.env['res.partner'].create({'name': 'partner a'})
        cls.partner_b = cls.env['res.partner'].create({'name': 'partner b'})
        cls.partner_c = cls.env['res.partner'].create({'name': 'partner c'})
        
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        
        # Create products to repair
        cls.product_to_repair1 = cls.env['product.product'].create({
            'name': 'Product To Repair 1',
            'type': 'product',
            'tracking': 'lot',
            'default_code': 'PRODUCT001'
        })
        cls.product_to_repair2 = cls.env['product.product'].create({
            'name': 'Product To Repair 2',
            'type': 'product',
            'default_code': 'PRODUCT002'
        })
        cls.product_to_repair3 = cls.env['product.product'].create({
            'name': 'Product To Repair 3',
            'type': 'product',
            'tracking': 'lot',
            'default_code': 'PRODUCT003'
        })
        cls.product_to_repair4 = cls.env['product.product'].create({
            'name': 'Product To Repair 4',
            'type': 'product',
            'default_code': 'PRODUCT004'
        })
        cls.product_to_repair5 = cls.env['product.product'].create({
            'name': 'Product To Repair 5',
            'type': 'product',
            'default_code': 'PRODUCT005'
        })
        
        # Create products used to repair
        cls.product_consu1 = cls.env['product.product'].create({
            'name': 'Consumer Product 1',
            'type': 'consu',
            'default_code': 'CONSUMPART001'
        })
        cls.product_consu2 = cls.env['product.product'].create({
            'name': 'Consumer Product 2',
            'type': 'consu',
            'default_code': 'CONSUMPART002'
        })
        cls.product_consu3 = cls.env['product.product'].create({
            'name': 'Consumer Product 3',
            'type': 'consu',
            'default_code': 'CONSUMPART003'
        })
        cls.product_consu4 = cls.env['product.product'].create({
            'name': 'Consumer Product 4',
            'type': 'consu',
            'default_code': 'CONSUMPART004'
        })
        cls.product_consu5 = cls.env['product.product'].create({
            'name': 'Consumer Product 5',
            'type': 'consu',
            'default_code': 'CONSUMPART005'
        })
        
        cls.product_product1 = cls.env['product.product'].create({
            'name': 'Storable Product 1',
            'type': 'product',
            'default_code': 'PRODUCTPART001'
        })
        cls.product_product2 = cls.env['product.product'].create({
            'name': 'Storable Product 2',
            'type': 'product',
            'default_code': 'PRODUCTPART002'
        })
        cls.product_product3 = cls.env['product.product'].create({
            'name': 'Storable Product 3',
            'type': 'product',
            'default_code': 'PRODUCTPART003'
        })
        cls.product_product4 = cls.env['product.product'].create({
            'name': 'Storable Product 4',
            'type': 'product',
            'default_code': 'PRODUCTPART004'
        })
        cls.product_product5 = cls.env['product.product'].create({
            'name': 'Storable Product 5',
            'type': 'product',
            'default_code': 'PRODUCTPART005'
        })
        
        # Create service products used to repair
        cls.product_service1 = cls.env['product.product'].create({
            'name': 'Product Service 1',
            'type': 'service'
        })
        cls.product_service2 = cls.env['product.product'].create({
            'name': 'Product Service 2',
            'type': 'service'
        })
        cls.product_service3 = cls.env['product.product'].create({
            'name': 'Product Service 3',
            'type': 'service'
        })
        
        # Create lots of repair products
        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': cls.product_to_repair1.id,
            'company_id': cls.env.company.id,
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'name': 'lot2',
            'product_id': cls.product_to_repair2.id,
            'company_id': cls.env.company.id,
        })
        cls.lot3 = cls.env['stock.production.lot'].create({
            'name': 'lot3',
            'product_id': cls.product_to_repair3.id,
            'company_id': cls.env.company.id,
        })
        
        # Create repair order
        cls.repair1 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair1.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_a.id,
            'repair_date': fields.Date.from_string('2021-08-27'),
            'guarantee_limit': fields.Date.from_string('2022-08-27'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': cls.partner_a.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'partner_id': cls.partner_a.id,
            'lot_id': cls.lot1.id,
            'company_id': cls.company.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product 1',
                    'type': 'add',
                    'product_id': cls.product_consu1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 100,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_consu1.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product 1',
                    'type': 'add',
                    'product_id': cls.product_product1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_product1.property_stock_production.id,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': 'Product Service 1',
                    'product_id': cls.product_service1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                })
            ]
        })
        
        cls.repair2 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair2.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_b.id,
            'repair_date': fields.Date.from_string('2021-08-28'),
            'guarantee_limit': fields.Date.from_string('2022-08-28'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': cls.partner_b.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'partner_id': cls.partner_b.id,
            'company_id': cls.company.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product 2',
                    'type': 'add',
                    'product_id': cls.product_consu2.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_consu2.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product 2',
                    'type': 'add',
                    'product_id': cls.product_product2.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_product2.property_stock_production.id,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': 'Product Service 2',
                    'product_id': cls.product_service2.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                })
            ]
        })
        
        cls.repair3 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair3.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_c.id,
            'repair_date': fields.Date.from_string('2021-08-29'),
            'guarantee_limit': fields.Date.from_string('2022-08-29'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': cls.partner_c.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'partner_id': cls.partner_c.id,
            'lot_id': cls.lot3.id,
            'company_id': cls.company.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product 3',
                    'type': 'add',
                    'product_id': cls.product_consu3.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 100,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_consu3.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product 2',
                    'type': 'add',
                    'product_id': cls.product_product3.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_product3.property_stock_production.id,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': 'Product Service 3',
                    'product_id': cls.product_service3.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 250,
                })
            ]
        })
        
        cls.repair4 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair4.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_a.id,
            'repair_date': fields.Date.from_string('2021-08-30'),
            'guarantee_limit': fields.Date.from_string('2022-08-30'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': cls.partner_a.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'partner_id': cls.partner_a.id,
            'company_id': cls.company.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product 4',
                    'type': 'add',
                    'product_id': cls.product_consu4.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 120,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_consu4.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product 4',
                    'type': 'add',
                    'product_id': cls.product_product4.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 230,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_product4.property_stock_production.id,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': 'Product Service 1',
                    'product_id': cls.product_service1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                })
            ]
        })
        
        cls.repair5 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair5.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_c.id,
            'repair_date': fields.Date.from_string('2021-08-31'),
            'guarantee_limit': fields.Date.from_string('2022-08-31'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': cls.partner_c.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'partner_id': cls.partner_c.id,
            'company_id': cls.company.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product 5',
                    'type': 'add',
                    'product_id': cls.product_consu5.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 250,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_consu5.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product 5',
                    'type': 'add',
                    'product_id': cls.product_product5.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_product5.property_stock_production.id,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': 'Product Service 2',
                    'product_id': cls.product_service2.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                })
            ]
        })
        
        cls.repair6 = cls.env['repair.order'].create({
            'product_id': cls.product_to_repair1.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_a.id,
            'repair_date': fields.Date.from_string('2021-08-31'),
            'guarantee_limit': fields.Date.from_string('2022-08-31'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': cls.partner_a.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'partner_id': cls.partner_a.id,
            'lot_id': cls.lot1.id,
            'company_id': cls.company.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product 1',
                    'type': 'add',
                    'product_id': cls.product_consu1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 100,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_consu1.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product 1',
                    'type': 'add',
                    'product_id': cls.product_product1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 200,
                    'location_id': cls.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': cls.product_product1.property_stock_production.id,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': 'Product Service 1',
                    'product_id': cls.product_service1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.uom_unit.id,
                    'price_unit': 150,
                })
            ]
        })
