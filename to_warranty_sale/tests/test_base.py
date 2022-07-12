from odoo.addons.to_warranty_management.tests.test_base import TestBase


class TestBase(TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()

        Users = cls.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True, 'tracking_disable': True})

        cls.user_salesman_user = Users.create({
            'name': 'Sale User',
            'login': 'sale_user',
            'email': 'user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_salesman').id])]
        })

        cls.customer = cls.env['res.partner'].create({'name': 'customer1'})
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.pricelist_usd = cls.env['product.pricelist'].create({
            'name': 'USD pricelist',
            'active': True,
            'currency_id': cls.env.ref('base.USD').id,
            'company_id': cls.env.company.id,
        })

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

        cls.so1 = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'partner_invoice_id': cls.customer.id,
            'partner_shipping_id': cls.customer.id,
            'pricelist_id': cls.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'product_uom': cls.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                }),
                (0, 0, {
                    'name': cls.product2.name,
                    'product_id': cls.product2.id,
                    'product_uom': cls.uom_unit.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 200.0,
                }),
            ],
        })

        cls.so2 = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'partner_invoice_id': cls.customer.id,
            'partner_shipping_id': cls.customer.id,
            'pricelist_id': cls.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'product_uom': cls.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                }),
            ],
        })

        cls.so3 = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'partner_invoice_id': cls.customer.id,
            'partner_shipping_id': cls.customer.id,
            'pricelist_id': cls.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product2.name,
                    'product_id': cls.product2.id,
                    'product_uom': cls.uom_unit.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 200.0,
                }),
            ],
        })

        cls.so4 = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'partner_invoice_id': cls.customer.id,
            'partner_shipping_id': cls.customer.id,
            'pricelist_id': cls.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product2.name,
                    'product_id': cls.product2.id,
                    'product_uom': cls.uom_unit.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 200.0,
                }),
            ],
        })
        cls.so1.action_confirm()
        cls.so2.action_confirm()
        cls.so3.action_confirm()
