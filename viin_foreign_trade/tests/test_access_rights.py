from odoo import fields
from odoo.tests import tagged, Form
from odoo.exceptions import AccessError

from .common import TestCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestCommon):

    def test_access_partner_form_view(self):
        try:
            p = self.foreign_trade_manager.partner_id.with_user(self.normal_user)
            with Form(p):
                pass
        except AccessError:
            self.fail("Normal Internal User should be able to read contact having user linked.")

    def test_access_right_stock_user(self):
        with Form(self.env['custom.declaration.export']) as f1:
            f1.sale_order_ids.add(self.so1)
            f1.request_date = fields.Date.from_string('2021-10-20')
        export_custom_declaration = f1.save()

        with Form(self.env['custom.declaration.import']) as f2:
            f2.purchase_order_ids.add(self.po1)
            f2.request_date = fields.Date.from_string('2021-10-20')
        import_custom_declaration = f2.save()

        with Form(import_custom_declaration) as f:
            with f.extra_expense_ids.new() as expense1:
                expense1.product_id = self.expense_product_1
                expense1.expense_value = 120
                expense1.split_method = 'equal'

        """
        [Security Test] - TC01

        - Case: Test access rights of stock user group on custom declaration import model
        - Expected Result: stock user group has read permission
            but doesn't have create/update/delete permissions on custom declaration import model
        """
        import_custom_declaration.with_user(self.stock_user).read(['id'])

        with self.assertRaises(AccessError):
            self.env['custom.declaration.import'].with_user(self.stock_user).create({
                'purchase_order_ids': [(0, 0, [self.po1.id])],
                'request_date': fields.Date.from_string('2021-10-20'),
                'stock_picking_ids': [(0, 0, [self.po1_picking1.id])],
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.with_user(self.stock_user).write({
                'stock_picking_ids': [(6, 0, [self.po1_picking2.id])]
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.with_user(self.stock_user).unlink()

        """
        [Security Test] - TC02

        - Case: Test access rights of stock user group on custom declaration export model
        - Expected Result: stock user group has read permission
            but doesn't have create/update/delete permissions on custom declaration export model
        """
        export_custom_declaration.with_user(self.stock_user).read(['id'])

        with self.assertRaises(AccessError):
            self.env['custom.declaration.export'].with_user(self.stock_user).create({
                'sale_order_ids': [(0, 0, [self.so1.id])],
                'request_date': fields.Date.from_string('2021-10-20'),
                'stock_picking_ids': [(0, 0, [self.so1_picking1.id])],
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.with_user(self.stock_user).write({
                'stock_picking_ids': [(6, 0, [self.so1_picking2.id])]
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.with_user(self.stock_user).unlink()

        """
        [Security Test] - TC03

        - Case: Test access rights of stock user group on custom declaration line model
        - Expected Result: stock user group has read permission
            but doesn't have create/update/delete permissions on custom declaration line model
        """
        export_custom_declaration.custom_declaration_line_ids.with_user(self.stock_user).read()
        import_custom_declaration.custom_declaration_line_ids.with_user(self.stock_user).read()

        with self.assertRaises(AccessError):
            self.env['custom.declaration.line'].with_user(self.stock_user).create({
                'product_id': self.import_product_1.id,
                'qty': 1.0,
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.custom_declaration_line_ids.with_user(self.stock_user).write({
                'qty': 1.0
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.custom_declaration_line_ids.with_user(self.stock_user).write({
                'qty': 1.0
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.custom_declaration_line_ids.with_user(self.stock_user).unlink()

        with self.assertRaises(AccessError):
            import_custom_declaration.custom_declaration_line_ids.with_user(self.stock_user).unlink()

        """
        [Security Test] - TC04

        - Case: Test access rights of stock user group on custom declaration tax import model
        - Expected Result: stock user group has read permission
            but doesn't have create/update/delete permissions on custom declaration tax import model
        """
        import_custom_declaration.tax_line_ids.with_user(self.stock_user).read()

        with self.assertRaises(AccessError):
            self.env['custom.declaration.tax.import'].with_user(self.stock_user).create({
                'product_id': self.import_product_1.id,
                'amount': 100.0,
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.tax_line_ids.with_user(self.stock_user).write({
                'amount': 100.0
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.tax_line_ids.with_user(self.stock_user).unlink()

        """
        [Security Test] - TC05

        - Case: Test access rights of stock user group on custom declaration tax export model
        - Expected Result: stock user group has read permission
            but doesn't have create/update/delete permissions on custom declaration tax export model
        """
        export_custom_declaration.tax_line_ids.with_user(self.stock_user).read()

        with self.assertRaises(AccessError):
            self.env['custom.declaration.tax.export'].with_user(self.stock_user).create({
                'product_id': self.import_product_1.id,
                'amount': 100.0,
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.tax_line_ids.with_user(self.stock_user).write({
                'amount': 100.0
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.tax_line_ids.with_user(self.stock_user).unlink()

        """
        [Security Test] - TC06

        - Case: Test access rights of stock user group on custom declaration tax import group model
        - Expected Result: stock user group has read permission
            but doesn't have create/update/delete permissions on custom declaration tax import group model
        """
        import_custom_declaration.custom_dec_tax_group_ids.with_user(self.stock_user).read()

        with self.assertRaises(AccessError):
            self.env['custom.declaration.tax.import.group'].with_user(self.stock_user).create({
                'tax_group_id': self.tax_group_import_1.id,
                'amount': 100.0,
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.custom_dec_tax_group_ids.with_user(self.stock_user).write({
                'amount': 100.0
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.custom_dec_tax_group_ids.with_user(self.stock_user).unlink()

        """
        [Security Test] - TC07

        - Case: Test access rights of stock user group on custom declaration tax export group model
        - Expected Result: stock user group has read permission
            but doesn't have create/update/delete permissions on custom declaration tax export group model
        """
        export_custom_declaration.custom_dec_tax_group_ids.with_user(self.stock_user).read()

        with self.assertRaises(AccessError):
            self.env['custom.declaration.tax.export.group'].with_user(self.stock_user).create({
                'tax_group_id': self.tax_group_import_1.id,
                'amount': 100.0,
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.custom_dec_tax_group_ids.with_user(self.stock_user).write({
                'amount': 100.0
            })

        with self.assertRaises(AccessError):
            export_custom_declaration.custom_dec_tax_group_ids.with_user(self.stock_user).unlink()

        # test for custom declaration line expense
        import_custom_declaration.extra_expense_ids.with_user(self.stock_user).read()

        with self.assertRaises(AccessError):
            self.env['custom.declaration.line.extra.expense'].with_user(self.stock_user).create({
                'product_id': self.expense_product_1.id,
                'expense_value': 120,
                'split_method': 'equal'
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.extra_expense_ids.with_user(self.stock_user).write({
                'expense_value': 100.0
            })

        with self.assertRaises(AccessError):
            import_custom_declaration.extra_expense_ids.with_user(self.stock_user).unlink()

    def test_access_right_foreign_trade_user(self):
        """
        [Security Test] - TC08

        - Case: Test access rights of foreign trade user group on custom declaration import model
        - Expected Result: foreign trade user group has create/read/update/delete permissions on custom declaration import model
        """
        with Form(self.env['custom.declaration.import'].with_user(self.foreign_trade_user)) as f2:
            f2.purchase_order_ids.add(self.po1)
            f2.request_date = fields.Date.from_string('2021-10-20')

        import_custom_declaration = f2.save()

        with Form(import_custom_declaration.with_user(self.foreign_trade_user)) as f:
            with f.extra_expense_ids.new() as expense1:
                expense1.product_id = self.expense_product_1
                expense1.expense_value = 120
                expense1.split_method = 'equal'

        import_custom_declaration.with_user(self.foreign_trade_user).read(['id'])

        import_custom_declaration.with_user(self.foreign_trade_user).write({
            'stock_picking_ids': [(6, 0, [self.po1_picking2.id])]
        })

        """
        [Security Test] - TC09

        - Case: Test access rights of foreign trade user group on custom declaration export model
        - Expected Result: foreign trade user group has create/read/update/delete permissions on custom declaration export model
        """
        with Form(self.env['custom.declaration.export'].with_user(self.foreign_trade_user)) as f1:
            f1.sale_order_ids.add(self.so1)
            f1.request_date = fields.Date.from_string('2021-10-20')

        export_custom_declaration = f1.save()

        export_custom_declaration.with_user(self.foreign_trade_user).read(['id'])

        export_custom_declaration.with_user(self.foreign_trade_user).write({
            'stock_picking_ids': [(6, 0, [self.so1_picking2.id])]
        })

        """
        [Security Test] - TC10

        - Case: Test access rights of foreign trade user group on custom declaration export model
        - Expected Result: foreign trade user group has create/read/update/delete permissions on custom declaration line model
        """
        import_custom_declaration.custom_declaration_line_ids.with_user(self.foreign_trade_user).write({
            'qty': 1.0
        })

        export_custom_declaration.custom_declaration_line_ids.with_user(self.foreign_trade_user).write({
            'qty': 1.0
        })

        """
        [Security Test] - TC11

        - Case: Test access rights of foreign trade user group on custom declaration tax import model
        - Expected Result: foreign trade user group has create/read/update/delete permissions on custom declaration tax import model
        """
        import_custom_declaration.tax_line_ids.with_user(self.foreign_trade_user).write({
            'amount': 100.0
        })

        """
        [Security Test] - TC12

        - Case: Test access rights of foreign trade user group on custom declaration tax export model
        - Expected Result: foreign trade user group has create/read/update/delete permissions on custom declaration tax export model
        """
        export_custom_declaration.tax_line_ids.with_user(self.foreign_trade_user).write({
            'amount': 100.0
        })

        """
        [Security Test] - TC13

        - Case: Test access rights of foreign trade user group on custom declaration tax import group model
        - Expected Result: foreign trade user group has create/read/update/delete permissions on
            custom declaration tax import group model
        """
        import_custom_declaration.custom_dec_tax_group_ids.with_user(self.foreign_trade_user).write({
            'amount': 100.0
        })

        """
        [Security Test] - TC14

        - Case: Test access rights of foreign trade user group on custom declaration tax export group model
        - Expected Result: foreign trade user group has create/read/update/delete permissions on
            custom declaration tax import group model
        """
        export_custom_declaration.custom_dec_tax_group_ids.with_user(self.foreign_trade_user).write({
            'amount': 100.0
        })

        # test access right for custom declaration line expense
        import_custom_declaration.extra_expense_ids.with_user(self.foreign_trade_user).write({
            'expense_value': 100.0
        })

        import_custom_declaration.with_user(self.foreign_trade_user).unlink()
        export_custom_declaration.with_user(self.foreign_trade_user).unlink()

    def test_access_right_multiple_companies(self):
        """
        [Security Test] - TC15

        - Case: Test access rights of multi-companies
        - Expected Result: foreign trade user can only access custom declaration of their company
        """
        with Form(self.env['custom.declaration.export'].with_user(self.foreign_trade_user)) as f1:
            f1.sale_order_ids.add(self.so1)
            f1.request_date = fields.Date.from_string('2021-10-20')

        export_custom_declaration = f1.save()

        with Form(self.env['custom.declaration.import'].with_user(self.foreign_trade_user)) as f2:
            f2.purchase_order_ids.add(self.po1)
            f2.request_date = fields.Date.from_string('2021-10-20')

        import_custom_declaration = f2.save()

        with self.assertRaises(AccessError):
            export_custom_declaration.with_user(self.foreign_trade_user_2).read(['id'])

        with self.assertRaises(AccessError):
            import_custom_declaration.with_user(self.foreign_trade_user_2).read(['id'])
