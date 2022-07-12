from odoo import fields
from odoo.tests import Form, tagged
from odoo.exceptions import UserError

from .common import TestCommon

@tagged('post_install', '-at_install')
class TestSaleOrder(TestCommon):

    def test_change_partner_on_so_01(self):
        """
        [Form Test] - TC12

        - Case: Create SO, which has partner is marked as foreign trade partner
        - Expected Result:
            + SO will be marked as foreign trade
        """
        with Form(self.env['sale.order']) as f:
            f.partner_id = self.foreign_trade_partner
            self.assertTrue(f.foreign_trade)


    def test_change_partner_on_so_02(self):
        """
        [Form Test] - TC13

        - Case: Update partner of SO to non foreign trade partner, while it is marked as foreign trade
        - Expected Result:
            + SO will not be marked as foreign trade
        """
        with Form(self.env['sale.order']) as f:
            f.partner_id = self.foreign_trade_partner

        so = f.save()
        with Form(so) as f:
            f.partner_id = self.partner_same_country
            self.assertTrue(not f.foreign_trade)

    def test_change_partner_on_so_03(self):
        """
        [Form Test] - TC14

        - Case: Create SO, which has partner is not marked as foreign trade partner
                but has country differ from country of current company
        - Expected Result:
            + SO will be marked as foreign trade
        """
        with Form(self.env['sale.order']) as f:
            f.partner_id = self.foreign_trade_partner_abnormal
            self.assertTrue(f.foreign_trade)

    def test_change_partner_on_so_04(self):
        """
        [Form Test] - TC15

        - Case: Update partner of SO to non foreign trade partner but has country differ from country of current company,
                 while it is not marked as foreign trade
        - Expected Result:
            + SO will be marked as foreign trade
        """
        with Form(self.env['sale.order']) as f:
            f.partner_id = self.partner_same_country

        so = f.save()
        with Form(so) as f:
            f.partner_id = self.foreign_trade_partner_abnormal
            self.assertTrue(f.foreign_trade)

    def test_create_so_01(self):
        """
        [Functional Test] - TC22

        - Case: Create SO, which has partner is marked as foreign trade partner
        - Expected Result:
            + SO will be marked as foreign trade
        """
        so = self.env['sale.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'partner_invoice_id': self.foreign_trade_partner.id,
            'partner_shipping_id': self.foreign_trade_partner.id,
            'pricelist_id': self.pricelist_eur.id,
        })
        self.assertTrue(so.foreign_trade)

    def test_create_so_02(self):
        """
        [Functional Test] - TC23

        - Case: Create SO, which has partner has country differ from country of SO company
        - Expected Result:
            + SO will be marked as foreign trade
        """
        so = self.env['sale.order'].create({
            'partner_id': self.foreign_trade_partner_abnormal.id,
            'partner_invoice_id': self.foreign_trade_partner_abnormal.id,
            'partner_shipping_id': self.foreign_trade_partner_abnormal.id,
            'pricelist_id': self.pricelist_eur.id,
        })
        self.assertTrue(so.foreign_trade)

    def test_custom_declaration_count_01(self):
        """
        [Functional Test] - TC24

        - Case: Check custom declaration count of SO, in case there is no custom declaration related to this SO
        - Expected Result:
            + custom declaration count of SO = 0
        """
        self.assertTrue(self.so1.custom_dec_count == 0)

    def test_custom_declaration_count_02(self):
        """
        [Functional Test] - TC25

        - Case: Check custom declaration count of SO, in case there are 2 custom declarations related to this SO
        - Expected Result:
            + custom declaration count of SO = 2
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            # f.stock_picking_id = self.so1_picking1

        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            # f.stock_picking_id = self.so1_picking2

        self.assertTrue(self.so1.custom_dec_count == 2)

    def test_custom_declaration_count_for_picking_01(self):
        """
        [Functional Test] - TC19

        - Case: Check export custom declaration count of picking, in case there is no export custom declaration related to this picking
        - Expected Result:
            + import custom declaration count of picking = 0
        """
        self.assertTrue(self.so1_picking1.custom_dec_export_count == 0)

    def test_custom_declaration_count_for_picking_02(self):
        """
        [Functional Test] - TC20

        - Case: Check export custom declaration count of picking, in case there are 2 export custom declarations related to this picking
        - Expected Result:
            + import custom declaration count of picking = 2
        """
        with Form(self.env['custom.declaration.export']) as f:
            # f.sale_order_id = self.so1
            f.stock_picking_ids.add(self.so1_picking1)

        with Form(self.env['custom.declaration.export']) as f:
            # f.sale_order_id = self.so1
            f.stock_picking_ids.add(self.so1_picking1)

        self.assertTrue(self.so1_picking1.custom_dec_export_count == 2)

    def test_custom_declaration_required_for_picking_01(self):
        """
        [Functional Test] - TC21

        - Case: Check import custom declaration required for picking, which has location destination is marked for custom clearance
            and there is no related custom declaration
        - Expected Result:
            + picking requires custom declaration
        """
        self.assertTrue(self.so1_picking1.custom_dec_required)
        self.assertTrue(self.so1_picking2.custom_dec_required)

    def test_flow_of_export_01(self):
        """
        [Functional Test] - TC49

        - Case: Operate export product to foreign partner
            + Delivery 1 step
        - Expected Result:
            + After confirm SO, there are 2 pickings are created,
            + 1st picking from stock to custom zone,
            + 2nd picking from custom zone to customer
            + Can't validate 2nd picking, while 1st picking doesn't have custom declaration, or custom declaration is not confirmed
        """
        self.env['stock.quant']._update_available_quantity(self.export_product_1, self.stock_location, 2)
        so = self.env['sale.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'partner_invoice_id': self.foreign_trade_partner.id,
            'partner_shipping_id': self.foreign_trade_partner.id,
            'pricelist_id': self.pricelist_eur.id,
            'order_line': [
                (0, 0, {
                    'name': self.export_product_1.name,
                    'product_id': self.export_product_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                    'tax_id': [(6, 0, [self.sale_tax.id])]
                })
            ],
        })
        so.action_confirm()
        so_picking1 = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)
        so_picking2 = so.picking_ids.filtered(lambda pk: pk.location_id == self.checked_warehouse.exp_custom_zone_loc_id)
        stock_move1 = so_picking1.move_lines[0]
        stock_move2 = so_picking2.move_lines[0]

        so_picking1.button_validate()
        so_picking1.action_confirm()
        so_picking1.action_assign()
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        so_picking1._action_done()

        so_picking2.button_validate()
        so_picking2.action_confirm()
        so_picking2.action_assign()
        stock_move2.move_line_ids.write({'qty_done': 2.0})
        with self.assertRaises(UserError):
            so_picking2._action_done()

        with Form(self.env['custom.declaration.export']) as f:
            f.stock_picking_ids.add(so_picking1)
            # f.sale_order_ids.add(so)
            f.request_date = fields.Date.from_string('2021-10-20')

        custom_declaration = f.save()

        with self.assertRaises(UserError):
            so_picking2._action_done()

        custom_declaration.action_open()
        custom_declaration.action_confirm()
        so_picking2._action_done()
        self.assertTrue(so_picking2.state == 'done')

    def test_flow_of_mto_01(self):
        """
        [Functional Test] - TC55

        - Case: Trigger MTO route when confirm SO
        - Expected Result:
            + After confirming SO, there is new PO is created,
            + When confirming PO, there are created 2 pickings
            + 1st picking from vendor to custom zone,
            + 2nd picking from custom zone to stock
        """
        # active MTO route because in odoo 14 MTO route is archived
        self.env.ref('stock.route_warehouse0_mto').active = True

        import_product = self.env['product.product'].create({
            'name': 'Test Import Product',
            'type': 'product',
            'categ_id': self.product_category_saleable.id,
            'import_tax_ids': [(6, 0, [self.tax_import_1.id, self.tax_import_2.id])],
            'route_ids': [(6, 0, [self.env.ref('viin_foreign_trade.route_warehouse0_import').id,
                                  self.env.ref('stock.route_warehouse0_mto').id])],
            'seller_ids': [
                (0, 0, {
                    'name': self.foreign_trade_partner.id,
                    'min_qty': 0.0,
                    'price': 100,
                    'currency_id': self.currency_usd.id,
                    'delay': 0,
                })
            ]
        })
        so = self.env['sale.order'].create({
            'partner_id': self.partner_same_country.id,
            'partner_invoice_id': self.partner_same_country.id,
            'partner_shipping_id': self.partner_same_country.id,
            'order_line': [
                (0, 0, {
                    'name': import_product.name,
                    'product_id': import_product.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 150.0,
                    'tax_id': [(6, 0, [self.sale_tax.id])]
                })
            ],
        })
        so.action_confirm()
        # find PO created from SO
        related_po = self.env['purchase.order'].search([('origin', '=', so.name)])
        self.assertTrue(related_po.foreign_trade)
        related_po.button_confirm()
        po_picking1 = related_po.picking_ids[0]
        po_picking2 = po_picking1.move_lines.move_dest_ids.picking_id
        self.assertTrue(all([po_picking1, po_picking2]))
        self.assertTrue(po_picking1.location_dest_id == self.checked_warehouse.imp_custom_zone_loc_id)
        self.assertTrue(po_picking2.location_id == self.checked_warehouse.imp_custom_zone_loc_id)

    def test_return_product_01(self):
        """
        [Functional Test] - TC57

        - Case: Return product from customer to stock
        - Expected Result:
            + After return product from customer to custom zone,
                the return from custom zone to stock will require custom declaration of previous return
        """
        self.env['stock.quant']._update_available_quantity(self.export_product_1, self.stock_location, 2)
        so = self.env['sale.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'partner_invoice_id': self.foreign_trade_partner.id,
            'partner_shipping_id': self.foreign_trade_partner.id,
            'pricelist_id': self.pricelist_eur.id,
            'order_line': [
                (0, 0, {
                    'name': self.export_product_1.name,
                    'product_id': self.export_product_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                    'tax_id': [(6, 0, [self.sale_tax.id])]
                })
            ],
        })
        so.action_confirm()
        so_picking1 = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)
        so_picking2 = so.picking_ids.filtered(lambda pk: pk.location_id == self.checked_warehouse.exp_custom_zone_loc_id)
        stock_move1 = so_picking1.move_lines[0]
        stock_move2 = so_picking2.move_lines[0]

        so_picking1.button_validate()
        so_picking1.action_confirm()
        so_picking1.action_assign()
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        so_picking1._action_done()

        so_picking2.button_validate()
        so_picking2.action_confirm()
        so_picking2.action_assign()
        stock_move2.move_line_ids.write({'qty_done': 2.0})

        with Form(self.env['custom.declaration.export']) as f:
            f.stock_picking_ids.add(so_picking1)
            # f.sale_order_id = so
            f.request_date = fields.Date.from_string('2021-10-20')

        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        so_picking2._action_done()
        self.assertTrue(so_picking2.state == 'done')

        # do return from picking 2
        with Form(self.env['stock.return.picking'].with_context({
            'default_picking_id': so_picking2
        })) as return_form:
            for idx in range(len(return_form.product_return_moves)):
                with return_form.product_return_moves.edit(idx) as line:
                    if line.product_id == self.export_product_1:
                        line.quantity = 2.0
        wizard = return_form.save()
        wizard = wizard.with_context({'default_picking_id': False})
        result = wizard._create_returns()
        return_picking1 = self.env['stock.picking'].browse(result[0])
        return_picking1.button_validate()
        return_picking1.action_confirm()
        return_picking1.action_assign()
        return_stock_move1 = return_picking1.move_lines[0]
        return_stock_move1.move_line_ids.write({'qty_done': 2.0})
        return_picking1._action_done()

        # do return from picking 1
        with Form(self.env['stock.return.picking'].with_context({
            'default_picking_id': so_picking1
        })) as return_form:
            for idx in range(len(return_form.product_return_moves)):
                with return_form.product_return_moves.edit(idx) as line:
                    if line.product_id == self.export_product_1:
                        line.quantity = 2.0
        wizard = return_form.save()
        wizard = wizard.with_context({'default_picking_id': False})
        result = wizard._create_returns()
        return_picking2 = self.env['stock.picking'].browse(result[0])
        return_picking2.button_validate()
        return_picking2.action_confirm()
        return_picking2.action_assign()
        return_stock_move2 = return_picking2.move_lines[0]
        return_stock_move2.move_line_ids.write({'qty_done': 2.0})
        with self.assertRaises(UserError):
            return_picking2._action_done()
