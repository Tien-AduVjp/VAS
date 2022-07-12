from odoo.tests.common import TransactionCase, tagged



@tagged('post_install', '-at_install')
class TestCommon(TransactionCase):
    
    def setUp(self):
        super(TestCommon, self).setUp()
        Partner = self.env['res.partner']
        Product = self.env['product.product']
        Picking = self.env['stock.picking']
        Stock_move = self.env['stock.move']
        self.partner1 = Partner.create({
            'name': 'Partner 1',
            'is_company': True,
            'street': '1888 Arbor Way',
            'city': 'Turlock',
            'state_id': self.env.ref('base.state_us_5').id,
            'country_id': self.env.ref('base.us').id,
            'email': 'partner1@example.viindoo.com'
            })
        self.driver = Partner.create({
            'name': 'Driver 1',
            'is_driver': True,
            'street': '55 Santa Barbara Rd',
            'city': 'Pleasant Hill',
            'state_id': self.env.ref('base.state_us_5').id,
            'country_id': self.env.ref('base.us').id,
            'email': 'driver1@example.viindoo.com'
            })
        self.vehicle = self.env['fleet.vehicle'].create({
            'license_plate': '1-BMW-999',
            'vin_sn': 99999,
            'model_id': self.env.ref('fleet.model_serie1').id,
            'driver_id': self.driver.id,
            'warning_volume': 40.0,
            'max_volume': 70.0,
            'warning_weight': 500.0,
            'max_weight': 1000.0,
            })
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.product1 = Product.create({
            'name': 'Product 1',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
            'weight': 10.0,
            'length': 1000.0,
            'width': 1000.0,
            'height': 1000.0,
            'stowage_factor': 0.7
        })
        self.picking = Picking.create({
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'partner_id': self.partner1.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'ready_for_fleet_picking': True,
        })
        self.stock_move = Stock_move.create({
            'name': 'Test Stock move 1',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'picking_id': self.picking.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 10.0,
        })
        self.trip = self.env['fleet.vehicle.trip'].create({
            'vehicle_id': self.vehicle.id,
            'driver_id': self.driver.id,
            'expected_start_date': '2020-01-01 12:00:00'
            })
