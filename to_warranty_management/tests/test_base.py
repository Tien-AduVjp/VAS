from odoo import fields
from odoo.tests import SavepointCase


class TestBase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.env.user.lang = 'en_US'

        Users = cls.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True, 'tracking_disable': True})
        # Create a users
        cls.user_user = Users.create({
            'name': 'Warranty User',
            'login': 'user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_warranty_management.group_warranty_user').id])]
        })
        # Create a warranty_user_read_purchase
        cls.user_read = Users.create({
            'name': 'Warranty User Purchase',
            'login': 'user1',
            'email': 'user1@example.com',
            'groups_id': [(6, 0, [cls.env.ref('to_warranty_purchase.group_warranty_user_read_purchase').id])]
        })

        cls.user_manager = Users.create({
            'name': 'Warranty Manager',
            'login': 'manager',
            'email': 'manager@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('to_warranty_management.group_warranty_manager').id])]
        })

        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test.partner@example.viindoo.com'
        })
        cls.milestone_30_days = cls.env['product.milestone'].create({
            'name': '30 days',
            'amount': 30,
            'uom_id': cls.env.ref('uom.product_uom_day').id
        })
        cls.milestone_15_days = cls.env['product.milestone'].create({
            'name': '15 days',
            'amount': 15,
            'uom_id': cls.env.ref('uom.product_uom_day').id
        })
        cls.milestone_1000_km = cls.env['product.milestone'].create({
            'name': '1000 km',
            'amount': 1000,
            'uom_id': cls.env.ref('uom.product_uom_km').id
        })
        cls.milestone_500_km = cls.env['product.milestone'].create({
            'name': '500 km',
            'amount': 500,
            'uom_id': cls.env.ref('uom.product_uom_km').id
        })
        cls.milestone_100_lit = cls.env['product.milestone'].create({
            'name': '100 lit',
            'amount': 100,
            'uom_id': cls.env.ref('uom.product_uom_litre').id
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'warranty_period': 12,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
            })]
        })
        cls.product_without_warranty_period = cls.env['product.product'].create({
            'name': 'Test Product Without Period',
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
            })]
        })
        cls.product_without_sale_apply = cls.env['product.product'].create({
            'name': 'Test Product Without Sale Apply',
            'warranty_period': 12,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_15_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_500_km.id,
                'apply_to': 'purchase',
            })]
        })
        cls.product_without_purchase_apply = cls.env['product.product'].create({
            'name': 'Test Product Without Purchase Apply',
            'warranty_period': 12,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
            })]
        })
        cls.warranty_claim = cls.env['warranty.claim'].create({
            'name': 'Test Warranty Claim',
            'product_id': cls.product.id,
            'partner_id': cls.partner.id,
            'type': 'customer',
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
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
            }), (0, 0, {
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
