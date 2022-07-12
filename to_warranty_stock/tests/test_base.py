from odoo import fields

from odoo.addons.to_warranty_management.tests.test_base import TestBase

class TestBase(TestBase):
    
    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        
        Users = cls.env['res.users'].with_context(no_reset_password=True)
        
        cls.user_stock_user = Users.create({
            'name': 'Stock User',
            'login': 'stock_user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('stock.group_stock_user').id])]
        })
        
        cls.product_serial1 = cls.env['product.product'].create({
            'name': 'Product Tracking Serial 1',
            'type': 'product',
            'tracking': 'serial',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'warranty_period': 24,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
            })]
        })
        cls.product_lot1 = cls.env['product.product'].create({
            'name': 'Product Tracking Lot 1',
            'type': 'product',
            'tracking': 'lot',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'warranty_period': 24,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
            })]
        })
        
        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'Test Lot 1',
            'product_id': cls.product_lot1.id,
            'company_id': cls.env.company.id,
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'warranty_period': 12,
            'warranty_claim_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
                'operation_start': 50,
                'current_measurement': 50
            }), (0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'sale',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'sale',
                'operation_start': 50,
                'current_measurement': 50
            })]
        })
        
        cls.lot_without_sale = cls.env['stock.production.lot'].create({
            'name': 'Test Lot Without Sale',
            'product_id': cls.product_lot1.id,
            'company_id': cls.env.company.id,
            'warranty_start_date': fields.Date.from_string('2021-08-23'),
            'warranty_period': 12,
            'warranty_claim_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
                'operation_start': 50,
                'current_measurement': 50
            })]
        })
        
        cls.lot_without_purchase = cls.env['stock.production.lot'].create({
            'name': 'Test Lot Without Purchase',
            'product_id': cls.product_lot1.id,
            'company_id': cls.env.company.id,
            'warranty_start_date': fields.Date.from_string('2021-08-23'),
            'warranty_period': 12,
            'warranty_claim_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'sale',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'sale',
                'operation_start': 50,
                'current_measurement': 50
            })]
        })
        
        cls.lot_without_expiration_date = cls.env['stock.production.lot'].create({
            'name': 'Test Lot Without Expiration Date',
            'product_id': cls.product_lot1.id,
            'company_id': cls.env.company.id,
            'warranty_period': 12,
            'warranty_claim_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
                'operation_start': 50,
                'current_measurement': 50
            })]
        })
