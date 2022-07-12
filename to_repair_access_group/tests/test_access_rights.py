from odoo import fields

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_base import TestBase


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestBase):

    def test_access_user_repair_manager(self):
        """
        [Security Test] TC05

        - Case: Test access rights of repair manager group on account tax model
        - Expected Result: repair manager group has read permission on account tax model
        """
        taxes = self.env['account.tax'].with_user(self.user_manager).search([])

        """
        [Security Test] TC06

        - Case: Test access rights of repair manager group on account tax model
        - Expected Result: repair manager group doesn't have create/update/delete permission on account tax model
        """
        if taxes:
            checked_tax = taxes[0]
            with self.assertRaises(AccessError):
                checked_tax.with_user(self.user_manager).write({'name': checked_tax.name})

            with self.assertRaises(AccessError):
                checked_tax.with_user(self.user_manager).unlink()

        with self.assertRaises(AccessError):
            self.env['account.tax'].with_user(self.user_manager).create({
                'name': 'new_tax',
                'amount_type': 'percent',
                'amount': 10,
            })

        """
        [Security Test] TC09

        - Case: Test access rights of repair manager group on repair tags model
        - Expected Result: repair manager group has full permissions on repair tags model
        """
        tag = self.env['repair.tags'].with_user(self.user_manager).create({
            'name': 'new tag',
        })

        tag.with_user(self.user_manager).read(['name'])
        tag.with_user(self.user_manager).write({'name': 'new tag 1'})
        tag.with_user(self.user_manager).unlink()

        """
        [Security Test] TC04

        - Case: Test access rights of repair manager group on stock production lot model
        - Expected Result: repair manager group has read permission on stock production lot model
        """
        lot = self.env['stock.production.lot']
        lot.with_user(self.user_manager).read(['name'])

        """
        [Security Test] TC01, TC02, TC03

        - Case: Test access rights of repair manager group on repair order, repair line, repair fee models
        - Expected Result: repair manager group has full permissions on repair order, repair line, repair fee models
        """
        repair = self.env['repair.order'].with_user(self.user_manager).create({
            'product_id': self.product_to_repair.id,
            'product_uom': self.uom_unit.id,
            'address_id': self.partner.id,
            'guarantee_limit': fields.Date.from_string('2021-08-30'),
            'invoice_method': 'b4repair',
            'partner_invoice_id': self.partner.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'partner_id': self.partner.id,
            'operations': [
                (0, 0, {
                    'name': 'Consumer Product',
                    'type': 'add',
                    'product_id': self.product_consu.id,
                    'product_uom_qty': 1,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100000,
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': self.product_consu.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Storable Product',
                    'type': 'add',
                    'product_id': self.product_product.id,
                    'product_uom_qty': 1,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 200000,
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
                    'price_unit': 250000,
                }),
                (0, 0, {
                    'name': 'Product Service 2',
                    'product_id': self.product_service2.id,
                    'product_uom_qty': 1,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150000,
                })
            ]
        })

        repair.operations.with_user(self.user_manager).read()
        repair.operations[0].with_user(self.user_manager).write({'price_unit': 150000})
        repair.operations[0].with_user(self.user_manager).unlink()

        repair.fees_lines.with_user(self.user_manager).read()
        repair.fees_lines[0].with_user(self.user_manager).write({'price_unit': 200000})
        repair.fees_lines[0].with_user(self.user_manager).unlink()

        repair.with_user(self.user_manager).read(['product_id'])
        repair.with_user(self.user_manager).write({'guarantee_limit': fields.Date.from_string('2021-08-31')})
        repair.with_user(self.user_manager).unlink()

        """
        [Security Test] TC07

        - Case: Test access rights of repair manager group on stock move model
        - Expected Result: repair manager group has create/read/update permissions on stock move model
        """
        stock_move = self.env['stock.move'].with_user(self.user_manager).create({
            'name': 'Test Stock Move',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id,
            'product_id': self.product_lot.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
        })

        stock_move.with_user(self.user_manager).read(['name', 'product_id'])

        stock_move.with_user(self.user_manager).write({'name': 'Test Stock Move Updated'})

        """
        [Security Test] TC08

        - Case: Test access rights of repair manager group on stock move model
        - Expected Result: repair manager group doesn't have delete permissions on stock move model
        """

        with self.assertRaises(AccessError):
            stock_move.with_user(self.user_manager).unlink()
