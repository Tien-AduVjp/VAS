from datetime import datetime

from odoo.addons.to_warranty_management.tests.test_base import TestBase


class TestBase(TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        cls.vendor1 = cls.env['res.partner'].create({'name': 'vendor1'})
        cls.vendor2 = cls.env['res.partner'].create({'name': 'vendor2'})
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

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
        cls.product_serial2 = cls.env['product.product'].create({
            'name': 'Product Tracking Serial 2',
            'type': 'product',
            'tracking': 'serial',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'warranty_period': 36,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
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
        cls.product_lot2 = cls.env['product.product'].create({
            'name': 'Product Tracking Lot 2',
            'type': 'product',
            'tracking': 'lot',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'warranty_period': 36,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_30_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': cls.milestone_1000_km.id,
                'apply_to': 'purchase',
            })]
        })

        # Create PO, confirm PO and their picking, stock move line
        cls.lot1 = cls.env['stock.production.lot'].create({
            'name': 'lot1_cls',
            'product_id': cls.product_lot1.id,
            'company_id': cls.env.company.id,
        })
        cls.lot2 = cls.env['stock.production.lot'].create({
            'name': 'lot2_cls',
            'product_id': cls.product_lot2.id,
            'company_id': cls.env.company.id,
        })

        cls.po1 = cls.env['purchase.order'].create({
            'partner_id': cls.vendor1.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product_lot1.name,
                    'product_id': cls.product_lot1.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': datetime.today(),
                })
            ],
        })
        cls.po1.button_confirm()
        picking1 = cls.po1.picking_ids[0]
        stock_move1 = picking1.move_lines[0]
        stock_move1.move_line_ids[0].lot_id = cls.lot1

        picking1.button_validate()
        stock_move1._action_confirm()
        stock_move1._action_assign()
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        stock_move1._action_done()

        cls.po2 = cls.env['purchase.order'].create({
            'partner_id': cls.vendor2.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product_lot2.name,
                    'product_id': cls.product_lot2.id,
                    'product_uom': cls.uom_unit.id,
                    'product_qty': 3.0,
                    'price_unit': 200.0,
                    'date_planned': datetime.today(),
                }),
            ],
        })
        cls.po2.button_confirm()
        picking2 = cls.po2.picking_ids[0]
        stock_move2 = picking2.move_lines[0]
        stock_move2.move_line_ids[0].lot_id = cls.lot2

        picking2.button_validate()
        stock_move2._action_confirm()
        stock_move2._action_assign()
        stock_move2.move_line_ids.write({'qty_done': 3.0})
        stock_move2._action_done()
