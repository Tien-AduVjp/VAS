from odoo import fields

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import TestCommon

@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestCommon):

    def test_access_warranty_user(self):
        """
        [Security Test] TC04

        - Case: Test access rights of warranty user group on account tax model
        - Expected Result: warranty user group has read permission on account tax model
        """
        taxes = self.env['account.tax'].with_user(self.warranty_user).search([])

        """
        [Security Test] TC05

        - Case: Test access rights of warranty user group on account tax model
        - Expected Result: warranty user group doesn't have create/update/delete permission on account tax model
        """
        if taxes:
            checked_tax = taxes[0]
            with self.assertRaises(AccessError):
                checked_tax.with_user(self.warranty_user).write({'name': checked_tax.name})

            with self.assertRaises(AccessError):
                checked_tax.with_user(self.warranty_user).unlink()

        with self.assertRaises(AccessError):
            self.env['account.tax'].with_user(self.warranty_user).create({
                'name': 'new_tax',
                'amount_type': 'percent',
                'amount': 10,
            })

        """
        [Security Test] TC08

        - Case: Test access rights of warranty user group on repair tags model
        - Expected Result: warranty user group has read permission on repair tags model
        """
        self.tag.with_user(self.warranty_user).read()

        """
        [Security Test] TC09

        - Case: Test access rights of warranty user group on repair tags model
        - Expected Result: warranty user group doesn't have create/update/delete permissions on repair tags model
        """
        with self.assertRaises(AccessError):
            self.tag.with_user(self.warranty_user).write({'name': 'new tag 1'})
            self.tag.with_user(self.warranty_user).unlink()

        with self.assertRaises(AccessError):
            self.env['repair.tags'].with_user(self.warranty_user).create({
                'name': 'new tag',
            })

        """
        [Security Test] TC01, TC02, TC03

        - Case: Test access rights of warranty user group on repair order, repair line, repair fee models
        - Expected Result: warranty user group has full permissions on repair order, repair line, repair fee models
        """
        repair = self.env['repair.order'].with_user(self.warranty_user).create({
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'address_id': self.partner_a.id,
            'guarantee_limit': fields.Date.from_string('2021-09-12'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': self.partner_a.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'partner_id': self.partner_a.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product',
                    'type': 'add',
                    'product_id': self.product_consu.id,
                    'product_uom_qty': 1,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': self.product_consu.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product',
                    'type': 'add',
                    'product_id': self.product_product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 200,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': self.product_product.property_stock_production.id,
                })
            ],
            'fees_lines': [
                (0, 0, {
                    'name': 'Product Service 1',
                    'product_id': self.product_service1.id,
                    'product_uom_qty': 1,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 250,
                }),
                (0, 0, {
                    'name': 'Product Service 2',
                    'product_id': self.product_service2.id,
                    'product_uom_qty': 1,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                })
            ]
        })

        repair.operations.with_user(self.warranty_user).read()
        repair.operations[0].with_user(self.warranty_user).write({'price_unit': 150})
        repair.operations[0].with_user(self.warranty_user).unlink()

        repair.fees_lines.with_user(self.warranty_user).read()
        repair.fees_lines[0].with_user(self.warranty_user).write({'price_unit': 200})
        repair.fees_lines[0].with_user(self.warranty_user).unlink()

        repair.with_user(self.warranty_user).read(['product_id'])
        repair.with_user(self.warranty_user).write({'guarantee_limit': fields.Date.from_string('2021-09-12')})
        repair.with_user(self.warranty_user).unlink()

        """
        [Security Test] TC06

        - Case: Test access rights of warranty user group on stock move model
        - Expected Result: warranty user group has read permissions on stock move model
        """
        stock_move = self.env['stock.move'].create({
            'name': 'Test Stock Move',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
        })

        stock_move.with_user(self.warranty_user).read(['id'])

        """
        [Security Test] TC07

        - Case: Test access rights of warranty user group on stock move model
        - Expected Result: warranty user group doesn't have create/update/delete permissions on stock move model
        """
        with self.assertRaises(AccessError):
            self.env['stock.move'].with_user(self.warranty_user).create({
                'name': 'Test Stock Move',
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                'product_id': self.product1.id,
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
                'picking_type_id': self.env.ref('stock.picking_type_internal').id,
            })

        with self.assertRaises(AccessError):
            stock_move.with_user(self.warranty_user).write({'name': 'Test Stock Move Updated'})

        with self.assertRaises(AccessError):
            stock_move.with_user(self.warranty_user).unlink()

        """
        [Security Test] TC10

        - Case: Test access rights of warranty user group on stock picking model
        - Expected Result: warranty user group has read permissions on stock picking model
        """
        picking = self.env['stock.picking'].create({
                'location_id': self.supplier_location.id,
                'location_dest_id': self.stock_location.id,
                'partner_id': self.partner_a.id,
                'picking_type_id': self.env.ref('stock.picking_type_in').id,
            })

        picking.with_user(self.warranty_user).read(['id'])

        """
        [Security Test] TC11

        - Case: Test access rights of warranty user group on stock picking model
        - Expected Result: warranty user group doesn't have create/update/delete permissions on stock picking model
        """
        with self.assertRaises(AccessError):
            self.env['stock.picking'].with_user(self.warranty_user).create({
                'location_id': self.supplier_location.id,
                'location_dest_id': self.stock_location.id,
                'partner_id': self.partner_a.id,
                'picking_type_id': self.env.ref('stock.picking_type_in').id,
            })

        with self.assertRaises(AccessError):
            picking.with_user(self.warranty_user).write({'partner_id': self.partner_b.id})

        with self.assertRaises(AccessError):
            picking.with_user(self.warranty_user).unlink()
