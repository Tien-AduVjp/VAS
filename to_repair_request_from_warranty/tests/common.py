from odoo import fields
from odoo.tests import SavepointCase

class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        # Create a users
        cls.warranty_user = cls.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'Warranty User',
            'login': 'warranty_user',
            'email': 'warranty_user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_warranty_management.group_warranty_user').id])]
        })

        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')

        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

        cls.partner_a = cls.env['res.partner'].create({
            'name': 'Test Partner A',
            'email': 'test.partnera@example.viindoo.com'
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'Test Partner B',
            'email': 'test.partnerb@example.viindoo.com'
        })
        cls.milestone_30_days = cls.env['product.milestone'].create({
            'name': '30 days',
            'amount': 30,
            'uom_id': cls.env.ref('uom.product_uom_day').id
        })
        cls.milestone_1000_km = cls.env['product.milestone'].create({
            'name': '1000 km',
            'amount': 1000,
            'uom_id': cls.env.ref('uom.product_uom_km').id
        })
        cls.product1 = cls.env['product.product'].create({
            'name': 'Test Product 1',
            'type': 'product',
            'tracking': 'lot',
            'warranty_period': 12,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
            })]
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'Test Product 2',
            'type': 'product',
            'tracking': 'lot',
            'warranty_period': 24,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
            })]
        })
        cls.product_consu = cls.env['product.product'].create({
            'name': 'Consumer Product',
            'type': 'consu'
        })
        cls.product_product = cls.env['product.product'].create({
            'name': 'Storable Product',
            'type': 'product'
        })
        cls.product_service1 = cls.env['product.product'].create({
            'name': 'Product Service 1',
            'type': 'service'
        })
        cls.product_service2 = cls.env['product.product'].create({
            'name': 'Product Service 2',
            'type': 'service'
        })

        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': cls.product1.id,
            'company_id': cls.env.company.id,
            'customer_id': cls.partner_a.id,
            'warranty_start_date': fields.Date.from_string('2021-09-06'),
            'warranty_period': 12,
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'name': 'lot2',
            'product_id': cls.product2.id,
            'company_id': cls.env.company.id,
            'customer_id': cls.partner_b.id,
            'warranty_start_date': fields.Date.from_string('2021-09-06'),
            'warranty_period': 24,
        })
        cls.warranty_claim1 = cls.env['warranty.claim'].create({
            'name': 'Test Warranty Claim 1',
            'product_id': cls.product1.id,
            'partner_id': cls.partner_a.id,
            'type': 'customer',
            'lot_id' : cls.lot1.id,
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
                'operation_start': 100,
                'current_measurement': 100
            })]
        })


        cls.warranty_claim2 = cls.env['warranty.claim'].create({
            'name': 'Test Warranty Claim 2',
            'product_id': cls.product2.id,
            'partner_id': cls.partner_b.id,
            'type': 'customer',
            'lot_id' : cls.lot2.id,
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
                'operation_start': 100,
                'current_measurement': 100
            })]
        })

        cls.warranty_claim3 = cls.env['warranty.claim'].create({
            'name': 'Test Warranty Claim 3',
            'product_id': cls.product2.id,
            'partner_id': cls.partner_b.id,
            'type': 'customer',
            'warranty_start_date': fields.Date.from_string('2021-09-06'),
            'warranty_period': 0,
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
                'operation_start': 100,
                'current_measurement': 100
            })]
        })

        cls.warranty_claim1.action_investigation()
        cls.warranty_claim1.action_confirm()
        cls.warranty_claim2.action_investigation()
        cls.warranty_claim2.action_confirm()
        cls.warranty_claim3.action_investigation()
        cls.warranty_claim3.action_confirm()

        cls.repair = cls.env['repair.order'].create({
            'product_id': cls.product2.id,
            'product_uom': cls.uom_unit.id,
            'address_id': cls.partner_b.id,
            'guarantee_limit': fields.Date.from_string('2023-09-06'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': cls.partner_b.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'partner_id': cls.partner_b.id,
            'warranty_claim_id': cls.warranty_claim2.id,
            'lot_id': cls.lot2.id
        })

        cls.tag = cls.env['repair.tags'].create({
                'name': 'test tag',
        })
