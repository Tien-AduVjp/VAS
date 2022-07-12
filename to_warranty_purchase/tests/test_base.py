from datetime import datetime

from odoo.tests import tagged
from odoo.addons.to_warranty_management.tests.test_base import TestBase


@tagged('post_install', '-at_install')
class TestBase(TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()

        Users = cls.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True, 'tracking_disable': True})

        cls.user_purchase_user = Users.create({
            'name': 'Purchase User',
            'login': 'purchase_user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('purchase.group_purchase_user').id])]
        })

        cls.vendor = cls.env['res.partner'].create({'name': 'vendor1'})
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

        cls.milestone_90_days = cls.env['product.milestone'].create({
            'name': '90 days',
            'amount': 90,
            'uom_id': cls.env.ref('uom.product_uom_day').id
        })
        cls.milestone_2000_km = cls.env['product.milestone'].create({
            'name': '2000 km',
            'amount': 2000,
            'uom_id': cls.env.ref('uom.product_uom_km').id
        })

        cls.product2 = cls.env['product.product'].create({
            'name': 'Test Product 2',
            'warranty_period': 24,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_90_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_2000_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_90_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_2000_km.id,
                'apply_to': 'purchase',
            })]
        })

        cls.product3 = cls.env['product.product'].create({
            'name': 'Test Product 3',
            'warranty_period': 18,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_90_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_2000_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_90_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_2000_km.id,
                'apply_to': 'purchase',
            })]
        })

        cls.po1 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': datetime.today(),
                }),
                (0, 0, {
                    'name': cls.product2.name,
                    'product_id': cls.product2.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 3.0,
                    'price_unit': 200.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })

        cls.po2 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 5.0,
                    'price_unit': 100.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })

        cls.po3 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product2.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 6.0,
                    'price_unit': 200.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })

        cls.po4 = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product2.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 6.0,
                    'price_unit': 200.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })
        cls.po1.button_confirm()
        cls.po2.button_confirm()
        cls.po3.button_confirm()
        cls.po4.button_cancel()
