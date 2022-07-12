from odoo.tests import tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestProductionLotWarrantyClaimPolicy(TestBase):

    def _compare_warranty_policies_for_lot_and_so_line(self, lot, so_line):
        claim_policy_for_lot = lot.warranty_claim_policy_ids
        policy_for_product = so_line.warranty_policy_ids
        if len(claim_policy_for_lot) == len(policy_for_product):
            set_claim_policy_for_lot = set()
            set_policy_for_product = set()
            for claim_policy in claim_policy_for_lot:
                set_claim_policy_for_lot.add((claim_policy.product_milestone_id.id, claim_policy.apply_to))
            for policy in policy_for_product:
                set_policy_for_product.add((policy.product_milestone_id.id, policy.apply_to))
            return set_claim_policy_for_lot == set_policy_for_product
        else:
            return False

    def test_stock_move_line_01(self):
        """
        [Functional Test] - TC01
        """
        lot1 = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.product_lot1.id,
            'company_id': self.env.company.id,
        })
        lot2 = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.product_lot2.id,
            'company_id': self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_lot1, self.stock_location, 2, lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product_lot2, self.stock_location, 3, lot_id=lot2)
        so = self.env['sale.order'].create({
            'partner_id': self.customer1.id,
            'partner_invoice_id': self.customer1.id,
            'partner_shipping_id': self.customer1.id,
            'pricelist_id': self.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_lot1.name,
                    'product_id': self.product_lot1.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                }),
                (0, 0, {
                    'name': self.product_lot2.name,
                    'product_id': self.product_lot2.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 150.0,
                })

            ],
        })
        so.action_confirm()
        picking = so.picking_ids[0]
        stock_move1 = picking.move_lines.filtered(lambda ml: ml.product_id == self.product_lot1)[0]
        stock_move2 = picking.move_lines.filtered(lambda ml: ml.product_id == self.product_lot2)[0]

        picking.button_validate()
        picking.move_lines._action_confirm()
        picking.move_lines._action_assign()
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        stock_move2.move_line_ids.write({'qty_done': 3.0})
        picking.move_lines._action_done()

        so_line1 = so.order_line.filtered(lambda line: line.product_id == self.product_lot1)[0]
        so_line2 = so.order_line.filtered(lambda line: line.product_id == self.product_lot2)[0]

        self.assertTrue(lot1.sale_order_id == so)
        self.assertTrue(lot2.sale_order_id == so)
        self.assertTrue(lot1.warranty_start_date == stock_move1.move_line_ids[0].date.date())
        self.assertTrue(lot2.warranty_start_date == stock_move2.move_line_ids[0].date.date())
        self.assertTrue(lot1.warranty_period == self.product_lot1.warranty_period)
        self.assertTrue(lot2.warranty_period == self.product_lot2.warranty_period)
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot1, so_line1))
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot2, so_line2))

    def test_stock_move_line_02(self):
        """
        [Functional Test] - TC02
        """
        lot1 = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.product_serial1.id,
            'company_id': self.env.company.id,
        })
        lot2 = self.env['stock.production.lot'].create({
            'name': 'lot2',
            'product_id': self.product_serial1.id,
            'company_id': self.env.company.id,
        })
        lot3 = self.env['stock.production.lot'].create({
            'name': 'lot3',
            'product_id': self.product_serial2.id,
            'company_id': self.env.company.id,
        })
        lot4 = self.env['stock.production.lot'].create({
            'name': 'lot4',
            'product_id': self.product_serial2.id,
            'company_id': self.env.company.id,
        })
        lot5 = self.env['stock.production.lot'].create({
            'name': 'lot5',
            'product_id': self.product_serial2.id,
            'company_id': self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_serial1, self.stock_location, 1, lot_id=lot1)
        self.env['stock.quant']._update_available_quantity(self.product_serial1, self.stock_location, 1, lot_id=lot2)
        self.env['stock.quant']._update_available_quantity(self.product_serial2, self.stock_location, 1, lot_id=lot3)
        self.env['stock.quant']._update_available_quantity(self.product_serial2, self.stock_location, 1, lot_id=lot4)
        self.env['stock.quant']._update_available_quantity(self.product_serial2, self.stock_location, 1, lot_id=lot5)
        so = self.env['sale.order'].create({
            'partner_id': self.customer1.id,
            'partner_invoice_id': self.customer1.id,
            'partner_shipping_id': self.customer1.id,
            'pricelist_id': self.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_serial1.name,
                    'product_id': self.product_serial1.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                }),
                (0, 0, {
                    'name': self.product_serial2.name,
                    'product_id': self.product_serial2.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 200.0,
                })
            ],
        })
        so.action_confirm()
        picking = so.picking_ids[0]
        stock_move1 = picking.move_lines.filtered(lambda ml: ml.product_id == self.product_serial1)[0]
        stock_move2 = picking.move_lines.filtered(lambda ml: ml.product_id == self.product_serial2)[0]

        picking.button_validate()
        picking.move_lines._action_confirm()
        picking.move_lines._action_assign()
        picking.move_lines.move_line_ids.write({'qty_done': 1.0})
        picking.move_lines._action_done()

        so_line1 = so.order_line.filtered(lambda line: line.product_id == self.product_serial1)[0]
        so_line2 = so.order_line.filtered(lambda line: line.product_id == self.product_serial2)[0]
        self.assertTrue(lot1.sale_order_id == so)
        self.assertTrue(lot2.sale_order_id == so)
        self.assertTrue(lot3.sale_order_id == so)
        self.assertTrue(lot4.sale_order_id == so)
        self.assertTrue(lot5.sale_order_id == so)
        self.assertTrue(lot1.warranty_start_date == stock_move1.move_line_ids[0].date.date())
        self.assertTrue(lot2.warranty_start_date == stock_move1.move_line_ids[1].date.date())
        self.assertTrue(lot3.warranty_start_date == stock_move2.move_line_ids[0].date.date())
        self.assertTrue(lot4.warranty_start_date == stock_move2.move_line_ids[1].date.date())
        self.assertTrue(lot5.warranty_start_date == stock_move2.move_line_ids[2].date.date())
        self.assertTrue(lot1.warranty_period == self.product_serial1.warranty_period)
        self.assertTrue(lot2.warranty_period == self.product_serial1.warranty_period)
        self.assertTrue(lot3.warranty_period == self.product_serial2.warranty_period)
        self.assertTrue(lot4.warranty_period == self.product_serial2.warranty_period)
        self.assertTrue(lot5.warranty_period == self.product_serial2.warranty_period)
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot1, so_line1))
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot2, so_line1))
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot3, so_line2))
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot4, so_line2))
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot5, so_line2))

    def test_stock_move_line_03(self):
        """
        [Functional Test] - TC03
        """
        lot1 = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.product_lot1.id,
            'company_id': self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_lot1, self.stock_location, 2, lot_id=lot1)
        so = self.env['sale.order'].create({
            'partner_id': self.customer1.id,
            'partner_invoice_id': self.customer1.id,
            'partner_shipping_id': self.customer1.id,
            'pricelist_id': self.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_lot1.name,
                    'product_id': self.product_lot1.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                })
            ],
        })
        so.action_confirm()
        picking = so.picking_ids[0]
        stock_move = picking.move_lines[0]

        picking.button_validate()
        stock_move._action_confirm()
        stock_move._action_assign()
        stock_move.move_line_ids.write({'qty_done': 2.0})
        stock_move._action_done()

        self.assertTrue(lot1.sale_order_id == so)
        self.assertTrue(lot1.warranty_start_date == stock_move.move_line_ids[0].date.date())
        self.assertTrue(lot1.warranty_period == self.product_lot1.warranty_period)
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot1, so.order_line[0]))

        # Change warranty policy on product
        current_warranty_policy_vals = []
        current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                                            'apply_to': 'sale'}))
        self.product_lot1.write({'warranty_policy_ids': current_warranty_policy_vals})
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot1, so.order_line[0]))

    def test_stock_move_line_04(self):
        """
        [Functional Test] - TC04
        """
        lot1 = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.product_lot1.id,
            'company_id': self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(self.product_lot1, self.stock_location, 2, lot_id=lot1)
        so = self.env['sale.order'].create({
            'partner_id': self.customer1.id,
            'partner_invoice_id': self.customer1.id,
            'partner_shipping_id': self.customer1.id,
            'pricelist_id': self.pricelist_usd.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_lot1.name,
                    'product_id': self.product_lot1.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                })
            ],
        })
        so.action_confirm()
        picking = so.picking_ids[0]
        stock_move = picking.move_lines[0]

        # Change warranty policy on product
        current_warranty_policy_vals = []
        current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                                            'apply_to': 'sale'}))
        self.product_lot1.write({'warranty_policy_ids': current_warranty_policy_vals})

        picking.button_validate()
        stock_move._action_confirm()
        stock_move._action_assign()
        stock_move.move_line_ids.write({'qty_done': 2.0})
        stock_move._action_done()

        self.assertTrue(lot1.sale_order_id == so)
        self.assertTrue(lot1.warranty_start_date == stock_move.move_line_ids[0].date.date())
        self.assertTrue(lot1.warranty_period == self.product_lot1.warranty_period)
        self.assertTrue(self._compare_warranty_policies_for_lot_and_so_line(lot1, so.order_line[0]))
