from odoo.tests import Form, tagged
from odoo.addons.mrp.tests.common import TestMrpCommon


@tagged('post_install', '-at_install')
class TestUnbuildBomWithPercentage(TestMrpCommon):

    @classmethod
    def setUpClass(cls):
        super(TestUnbuildBomWithPercentage, cls).setUpClass()

        cls.partner_id = cls.env.ref('base.partner_admin').id
        cls.pothos_office = cls.env['product.product'].create({'name': 'Pothos plant for office', 'type': 'product'})
        cls.pothos_plant_without_pot = cls.env['product.product'].create({'name': 'Pothos plant (without pot)', 'type': 'product'})
        cls.big_plant_pot = cls.env['product.product'].create({'name': 'Big plant pot', 'type': 'product'})
        cls.soil_for_plant = cls.env['product.product'].create({'name': 'Rich soil', 'type': 'product'})
        cls.bom_pothos = cls.env['mrp.bom'].create({
            'product_id': cls.pothos_office.id,
            'product_qty': 1.0,
            'product_tmpl_id': cls.pothos_office.product_tmpl_id.id,
            'type': 'normal',
            'bom_line_ids': [
                (0, 0, {'product_id': cls.pothos_plant_without_pot.id, 'product_qty': 1, 'price_percent': 75}),
                (0, 0, {'product_id': cls.big_plant_pot.id, 'product_qty': 1, 'price_percent': 15}),
                (0, 0, {'product_id': cls.soil_for_plant.id, 'product_qty': 2, 'price_percent': 10})
        ]})

    # =============================================== HELPERS ===================================================== #

    def _create_confirm_order_and_validate_the_receipt(self, order_line_data_list):
        test_order = self.env['purchase.order'].create({'partner_id': self.partner_id})

        # Update fields on order line data
        for data in order_line_data_list:
            data['date_planned'] = test_order.date_order
            data['order_id'] = test_order.id

        self.env['purchase.order.line'].create(order_line_data_list)

        test_order.button_confirm()

        # Receipt of this order - simulate the received receipt with "done" quantity
        test_receipt = test_order.picking_ids[0]
        move_lines_on_test_receipt = test_receipt.move_lines

        for move_line in move_lines_on_test_receipt:
            qty_done = move_line.quantity_done
            prod_uom_qty = move_line.product_uom_qty
            if qty_done != prod_uom_qty:
                move_line.write({'quantity_done': prod_uom_qty})

        # Validate this receipt (Stock picking)
        test_receipt.button_validate()

        return (test_order, test_receipt)

    def _create_unbuild_order(self):
        f = Form(self.env['mrp.unbuild'])
        f.product_id = self.pothos_office
        f.bom_id = self.bom_pothos
        f.product_uom_id = self.uom_unit
        f.product_qty = 1
        test_unbuild_order = f.save()
        test_unbuild_order.action_validate()
        return test_unbuild_order

    def _retrieve_actual_price_for_products_as_components(self, unbuild_order):
        #    From unbuild order => Product moves (stock.move) => stock valuation layer

        # svl = stock valuation layer
        # .produce_line_id returns related stock_moves
        related_svl = unbuild_order.produce_line_ids.mapped('stock_valuation_layer_ids')
        related_svl_product_components = related_svl.filtered(lambda svl: svl.product_id.id != self.pothos_office.id)

        res = {}
        for svl in related_svl_product_components:
            this_bom_line = self.bom_pothos.bom_line_ids.filtered(lambda r1: svl.product_id.id == r1.product_id.id)
            res[svl.product_id.id] = {
                'product': svl.product_id,
                'price_percent': this_bom_line.price_percent,
                'value': svl.value
            }

        return res

    # ============================================== TEST CASES =================================================== #

    def test_03_unbuild_bom_percentage_standard_price(self):
        """
            Test case having products setup with:
                costing method: standard price
                cost: != 0 (all products have initial cost - standard_price)

            The cost of the product components will be assigned:
                - according the initial cost on the product itself
                - not based on the percentage
        """

        self.pothos_office.write({'standard_price': 100, 'categ_id': self.env.ref('product.product_category_1').id})
        self.pothos_plant_without_pot.write({'standard_price': 50, 'categ_id': self.env.ref('product.product_category_1').id})
        self.big_plant_pot.write({'standard_price': 35, 'categ_id': self.env.ref('product.product_category_1').id})
        self.soil_for_plant.write({'standard_price': 15, 'categ_id': self.env.ref('product.product_category_1').id})

        operation_type_receipts = self.env.ref('stock.picking_type_in')
        stock_location_id = self.env['ir.model.data'].xmlid_to_object('stock.stock_location_stock').id
        receipt_destination_location_id = operation_type_receipts.default_location_dest_id.id

        self.env['stock.quant'].create({
            'product_id': self.pothos_office.id,
            'location_id': stock_location_id,
            'inventory_quantity': 2
        })

        # Create a transfer order (stock picking)
        test_stock_picking = self.env['stock.picking'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'picking_type_id': operation_type_receipts.id,
            'location_id': stock_location_id,
            'location_dest_id': receipt_destination_location_id,
            'move_ids_without_package': [
                (0, 0, {
                    'name': 'Pothos move in',
                    'location_id': stock_location_id,
                    'location_dest_id': receipt_destination_location_id,
                    'product_id': self.pothos_office.id,
                    'product_uom': 1,
                    'product_uom_qty': 1,
                    'quantity_done': 1,
                    }
                )
            ]
        })

        test_stock_picking.action_confirm()
        test_stock_picking.button_validate()

        # Unbuild order
        f = Form(self.env['mrp.unbuild'])
        f.product_id = self.pothos_office
        f.bom_id = self.bom_pothos
        f.product_uom_id = self.uom_unit
        f.product_qty = 1
        test_unbuild_order = f.save()

        # Use action_unbuild, not action_validate for quick test,
        # because we haven't produced the product yet, so there is no real product in stock (the available quantity is 0)
        test_unbuild_order.action_unbuild()

        actual_result = self._retrieve_actual_price_for_products_as_components(test_unbuild_order)

        self.assertEqual(
            actual_result[self.pothos_plant_without_pot.id]['value'],
            50,
            "Error testing: the cost value for 'Pothos Plant Without Pot' in Inventory Valuation shoud 50, not according to the percentage of 75.",
        )
        self.assertEqual(
            actual_result[self.big_plant_pot.id]['value'],
            35,
            "Error testing: the cost value for 'Big Plant Pot' in Inventory Valuation shoud 35, not according to the percentage of 15.",
        )
        self.assertEqual(
            actual_result[self.soil_for_plant.id]['value'],
            30,
            "Error testing: the cost value for 'Rich Soil' in Inventory Valuation shoud 30 for 2 packs, not according to the percentage of 10.",
        )

    def test_04_unbuild_bom_percentage_product_fifo(self):
        """
            cost method: First In First Out (FIFO)
            The cost of the product components will be computed based on the percentage setup on the BoM
        """

        fifo_category = self.env['product.category'].create({'name': 'Outlet FIFO', 'parent_id': 1, 'property_cost_method': 'fifo'})
        self.pothos_office.write({'categ_id': fifo_category.id})
        self.pothos_plant_without_pot.write({'categ_id': fifo_category.id})
        self.big_plant_pot.write({'categ_id': fifo_category.id})
        self.soil_for_plant.write({'categ_id': fifo_category.id})

        order_line_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 10,
                'product_uom': 1,
                'price_unit': 1000000,
            }
        ]
        _, test_receipt = self._create_confirm_order_and_validate_the_receipt(order_line_data)

        self.assertEqual(
            test_receipt.move_ids_without_package.stock_valuation_layer_ids.value,
            10000000,
            "Error testing: Pothos Office should be recorded with the cost 10.000.000 for quantity 10 in Inventory Valuation."
        )

        test_unbuild_order = self._create_unbuild_order()

        actual_result = self._retrieve_actual_price_for_products_as_components(test_unbuild_order)

        self.assertEqual(
            actual_result[self.pothos_plant_without_pot.id]['value'],
            750000,
            "Error testing: The cost of Pothos Plan Without Pot should be 750.000 after unbuilding the order"
        )
        self.assertEqual(
            actual_result[self.big_plant_pot.id]['value'],
            150000,
            "Error testing: The cost of Big Plant Pot should be 150.000 after unbuilding the order"
        )
        self.assertEqual(
            actual_result[self.soil_for_plant.id]['value'],
            100000,
            "Error testing: The cost of Rich Soil should be 100.000 after unbuilding the order"
        )

    def test_05_unbuild_bom_percentage_average_cost_method(self):
        """
            cost method: Average Cost (AVCO)
            The cost of the product components will be computed based on the percentage setup on the BoM
        """
        avco_category = self.env['product.category'].create({'name': 'Secondhand AVCO', 'parent_id': 1, 'property_cost_method': 'average'})
        self.pothos_office.write({'categ_id': avco_category.id})
        self.pothos_plant_without_pot.write({'categ_id': avco_category.id})
        self.big_plant_pot.write({'categ_id': avco_category.id})
        self.soil_for_plant.write({'categ_id': avco_category.id})

        order_line_data_1 = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 1000000,
            }
        ]
        order_line_data_2 = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 2',
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 1200000,
            }
        ]
        # With quantity = 1:
        # The average cost of the Pothos Office will be (1.000.000 + 1.200.000) / 2 = 1.100.000
        self._create_confirm_order_and_validate_the_receipt(order_line_data_1)
        self._create_confirm_order_and_validate_the_receipt(order_line_data_2)

        test_unbuild_order = self._create_unbuild_order()

        actual_result = self._retrieve_actual_price_for_products_as_components(test_unbuild_order)

        self.assertEqual(
            actual_result[self.pothos_plant_without_pot.id]['value'],
            825000,
            "Error testing: The cost of Pothos Plan Without Pot should be 825.000 (75% of 1.100.000) after unbuilding the order"
        )
        self.assertEqual(
            actual_result[self.big_plant_pot.id]['value'],
            165000,
            "Error testing: The cost of Big Plant Pot should be 165.000 (15% of 1.100.000) after unbuilding the order"
        )
        self.assertEqual(
            actual_result[self.soil_for_plant.id]['value'],
            110000,
            "Error testing: The cost of Rich Soil should be 110.000 (10% of 1.100.000) after unbuilding the order"
        )
