from odoo.tests import SavepointCase, tagged, Form


@tagged('-at_install', 'post_install')
class TestUnbuildPurchasedBomKit(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestUnbuildPurchasedBomKit, cls).setUpClass()

        cls.partner_id = cls.env.ref('base.partner_admin').id
        cls.partner_SO_id = cls.env.ref('base.res_partner_1').id

        cls.test_stock_location= cls.env.ref('stock.stock_location_stock')

        cls.test_fifo_category = cls.env.ref('product.product_category_5')
        cls.test_fifo_category.write({'property_cost_method': 'fifo', 'property_valuation': 'real_time'})

        # The products for creating Kit-type BoM must not have any Reordering Rule
        cls.pothos_office = cls.env.ref('product.product_product_10')
        cls.pothos_plant_without_pot = cls.env.ref('product.product_product_9')
        cls.big_plant_pot = cls.env.ref('mrp.product_product_wood_panel')
        cls.soil_for_plant = cls.env.ref('product.product_product_6')

        cls.bom_pothos = cls.env['mrp.bom'].create({
            'product_id': cls.pothos_office.id,
            'product_qty': 1.0,
            'product_tmpl_id': cls.pothos_office.product_tmpl_id.id,
            'type': 'phantom',
            'bom_line_ids': [
                (0, 0, {'product_id': cls.pothos_plant_without_pot.id, 'product_qty': 1, 'price_percent': 75}),
                (0, 0, {'product_id': cls.big_plant_pot.id, 'product_qty': 1, 'price_percent': 15}),
                (0, 0, {'product_id': cls.soil_for_plant.id, 'product_qty': 2, 'price_percent': 10})
        ]})

        cls.sn_count = 1

    # ================================================ HELPERS ==================================================== #

    def _create_confirm_order_and_validate_the_receipt(self, input_order_type, order_line_data_list, get_receipt=True):
        """
            Create an Purchase Order or Sales Order. Either case is depended on param input_order_type.

            :param: input_order_type         [string]:
            :param: order_line_data_list     [list]
        """
        test_order = False

        if input_order_type == 'PO':
            test_order = self.env['purchase.order'].with_context(tracking_disable=True).create({
                'partner_id': self.partner_id
                })

            # Update fields on order line data
            for data in order_line_data_list:
                data['date_planned'] = test_order.date_order
                data['order_id'] = test_order.id

            self.env['purchase.order.line'].create(order_line_data_list)

            test_order.button_confirm()

        if input_order_type == 'SO':
            test_order = self.env['sale.order'].with_context(tracking_disable=True).create({
                'partner_id': self.partner_SO_id,
                'order_line': order_line_data_list
            })

            test_order.write({'state': 'sent'})
            test_order.action_confirm()

        # Return the validated receipt
        if get_receipt:
            return self._get_receipt_to_validate(test_order) if test_order else self
        else:
            return test_order

    def _get_receipt_to_validate(self, input_order):
        """
            Simulate the received receipt with "done" quantity.
            The validation is processed using Form test in different cases:
                -    tracking / no tracking product

            :param: input_order              [self.env['purchase.order'] or self.env['sale.order']]

            :return: the receipt
        """

        test_receipt = input_order.picking_ids[0]

        # Receipt of this order - simulate the received receipt with "done" quantity
        for move_line in test_receipt.move_ids_without_package:
            if move_line.has_tracking == "serial":
                # fill up done quantity if product has tracking (Lot/Serial)
                # parameter view here is the wizard window asking to enter the seriah number
                move_form = Form(move_line, view='stock.view_stock_move_nosuggest_operations')
                for i in range(int(move_line.product_uom_qty)):
                    # generate new number of serial to satisfy the requirement - no duplicated serial
                    new_lot_seriah = 'PLANT000' + str(self.sn_count)
                    with move_form.move_line_nosuggest_ids.new() as line:
                        line.lot_name = new_lot_seriah

                    self.sn_count += 1
                move_line = move_form.save()
            else:
                # fill up done quantity if product has no tracking (Lot/Serial)
                qty_done = move_line.quantity_done
                prod_uom_qty = move_line.product_uom_qty
                if qty_done != prod_uom_qty:
                    move_line.write({'quantity_done': prod_uom_qty})

        # Validate this receipt (Stock picking)
        test_receipt.button_validate()

        return test_receipt

    def _retrieve_inventory_valuation_layer_components(self, test_receipt):
        """
            From receipt => Product moves (stock.move) => stock valuation layer

            :param: test_receipt    [stock.move]

            :return: res            [dict]
        """

        # svl = stock valuation layer
        related_svl = test_receipt.move_ids_without_package.stock_valuation_layer_ids
        related_svl_product_components = related_svl.filtered(lambda svl: svl.product_id.id != self.pothos_office.id)

        res = {}
        for svl in related_svl_product_components:
            # get the percentage in corresponding line from the BoM
            this_bom_line = self.bom_pothos.bom_line_ids.filtered(lambda r1: svl.product_id.id == r1.product_id.id)
            res[svl.product_id.id] = {
                'product': svl.product_id,
                'price_percent': this_bom_line[0].price_percent,
                'value': svl.value,
                'unit_cost': svl.unit_cost,
            }

        return res

    # ============================================== TEST CASES =================================================== #

    def test_02_TH1_product_no_lot_fifo_bom_kit_(self):
        """
            All products are None Tracking

            A - Received 1 pothos at 1.000.000:
                => pothos_no_pot:        1.000.000 * 0.75 = 750.000
                => pot:                  1.000.000 * 0.15 = 150.000
                => soil:                 1.000.000 * 0.1  = 100.000
            B - Received 2 pothos at 900.000:
                => pothos_no_pot:        900.000 * 0.75 * 2 = 1.350.000
                => pot:                  900.000 * 0.15 * 2 = 270.000
                => soil:                 900.000 * 0.1  * 2 = 180.000
            C - Delivered 1 pothos:
                => pothos_no_pot:        -750.000 (from A)
                => pot:                  -150.000 (from A)
                => soil:                 -100.000 (from A)
            D - Delivered 1 pothos_no_pot:
                => pot:                  -(270.000 / 2) = -135.000

        """

        self.pothos_plant_without_pot.write({'tracking': 'none'})
        self.big_plant_pot.write({'tracking': 'none'})
        self.soil_for_plant.write({'tracking': 'none'})

        # ========== TH1 - A ========== #

        purchase_order_line_1_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 1000000,
            }
        ]
        test_receipt_1 = self._create_confirm_order_and_validate_the_receipt('PO', purchase_order_line_1_data)
        res_1 = self._retrieve_inventory_valuation_layer_components(test_receipt_1)

        self.assertEqual(
            res_1[self.pothos_plant_without_pot.id]['value'],
            750000,
            "The cost of Pothos Plan Without Pot should be 750.000."
        )
        self.assertEqual(
            res_1[self.big_plant_pot.id]['value'],
            150000,
            "The cost of Big Plant Pot should be 150.000."
        )
        self.assertEqual(
            res_1[self.soil_for_plant.id]['value'],
            100000,
            "The cost of Rich Soil should be 100.000 for 2."
        )

        # ========== TH1 - B ========== #

        purchase_order_line_2_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 2,
                'product_uom': 1,
                'price_unit': 900000,
            }
        ]
        test_receipt_2 = self._create_confirm_order_and_validate_the_receipt('PO', purchase_order_line_2_data)
        res_2 = self._retrieve_inventory_valuation_layer_components(test_receipt_2)

        self.assertEqual(
            res_2[self.pothos_plant_without_pot.id]['value'],
            1350000,
            "The cost of Pothos Plan Without Pot should be 1.350.000 for 2."
        )
        self.assertEqual(
            res_2[self.big_plant_pot.id]['value'],
            270000,
            "The cost of Big Plant Pot should be 270.000 for 2."
        )
        self.assertEqual(
            res_2[self.soil_for_plant.id]['value'],
            180000,
            "The cost of Rich Soil should be 180.000 for 4."
        )

        # ========== TH1 - C ========== #

        sales_order_line_list = [
            (0, 0, {
                'name': self.pothos_office.name,
                'product_id': self.pothos_office.id,
                'product_uom_qty': 1,
            })
        ]
        test_receipt_3 = self._create_confirm_order_and_validate_the_receipt('SO', sales_order_line_list)
        res_3 = self._retrieve_inventory_valuation_layer_components(test_receipt_3)

        self.assertEqual(
            res_3[self.pothos_plant_without_pot.id]['value'],
            -750000,
            "The cost of Pothos Plan Without Pot should be 1.350.000 for 1."
        )
        self.assertEqual(
            res_3[self.big_plant_pot.id]['value'],
            -150000,
            "The cost of Big Plant Pot should be 270.000 for 1."
        )
        self.assertEqual(
            res_3[self.soil_for_plant.id]['value'],
            -100000,
            "The cost of Rich Soil should be 180.000 for 2."
        )

        # ========== TH1 - D - Separated sale ========== #

        sales_order_line_list = [
            (0, 0, {
                'product_id': self.big_plant_pot.id,
                'product_uom_qty': 1,
            }),
            (0, 0, {
                'product_id': self.soil_for_plant.id,
                'product_uom_qty': 1,
            })
        ]
        test_receipt_4 = self._create_confirm_order_and_validate_the_receipt('SO', sales_order_line_list)
        res_4 = self._retrieve_inventory_valuation_layer_components(test_receipt_4)

        self.assertEqual(
            res_4[self.big_plant_pot.id]['value'],
            -135000,
            "The cost of Pot Plant should be -135.000 for 1."
        )
        self.assertEqual(
            res_4[self.soil_for_plant.id]['value'],
            -45000,
            "The cost of Rich Soil should be -45.000 for 1."
        )

    def test_02_TH2_product_fifo_has_lot(self):
        """
            All products has tracking as Lot/Serial

            A - Received 1 pothos at 1.000.000:
                                                       value
                                                       -------
                => pothos_no_pot:   1.000.000 * 0.75 = 750.000
                => pot:             1.000.000 * 0.15 = 150.000
                => soil:            1.000.000 * 0.1  = 100.000
            B - Received 2 pothos at 899.000:
                                                         unit_cost        value
                                                         ---------        ---------
                => pothos_no_pot:   899.000 * 0.75 * 2 =   674.250 * 2 =  1.340.500
                => pot:             899.000 * 0.15 * 2 =   134.850 * 2 =  269.700
                => soil:            899.000 * 0.1  * 4 =    44.950 * 4 =  179.800
        """

        # ========== TH2 - A ========== #

        self.pothos_plant_without_pot.write({'tracking': 'serial'})
        self.big_plant_pot.write({'tracking': 'serial'})
        self.soil_for_plant.write({'tracking': 'serial'})

        purchase_order_line_1_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 1000000,
            }
        ]
        test_receipt_1 = self._create_confirm_order_and_validate_the_receipt('PO', purchase_order_line_1_data)
        res_1 = self._retrieve_inventory_valuation_layer_components(test_receipt_1)

        self.assertEqual(
            res_1[self.pothos_plant_without_pot.id]['value'],
            750000,
            "The cost of Pothos Plan Without Pot should be 750.000."
        )
        self.assertEqual(
            res_1[self.big_plant_pot.id]['value'],
            150000,
            "The cost of Big Plant Pot should be 150.000."
        )
        self.assertEqual(
            res_1[self.soil_for_plant.id]['value'],
            100000,
            "The cost of Rich Soil should be 100.000 for 2."
        )

        # ========== TH2 - B ========== #

        purchase_order_line_2_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 2',
                'product_qty': 2,
                'product_uom': 1,
                'price_unit': 899000,
            }
        ]
        test_receipt_2 = self._create_confirm_order_and_validate_the_receipt('PO', purchase_order_line_2_data)
        res_2 = self._retrieve_inventory_valuation_layer_components(test_receipt_2)

        self.assertEqual(
            res_1[self.pothos_plant_without_pot.id]['value'] + res_2[self.pothos_plant_without_pot.id]['value'],
            2098500,
            "The total value of all Pothos Plan Without Pot should be 750.000 + 1.340.500 = 2.090.500 after purchased twice."
        )
        self.assertEqual(
            res_1[self.big_plant_pot.id]['value'] + res_2[self.big_plant_pot.id]['value'],
            419700,
            "The total value of all Big Plant Pot should be 150.000 + 269.700 = 419.700 after purchased twice."
        )
        self.assertEqual(
            res_1[self.soil_for_plant.id]['value'] + res_2[self.soil_for_plant.id]['value'],
            279800,
            "The total value of all Rich Soil should be 100.000 + 179.800 = 279.800 after purchased twice."
        )

        # ========== TH2 - B2 ========== #

        self.assertEqual(
            res_2[self.pothos_plant_without_pot.id]['unit_cost'],
            674250,
            "The unit cost of Pothos Plan Without Pot should be 674.250 after purchased twice."
        )
        self.assertEqual(
            res_2[self.big_plant_pot.id]['unit_cost'],
            134850,
            "The cost of Big Plant Pot should be 134.850 after purchased twice."
        )
        self.assertEqual(
            res_2[self.soil_for_plant.id]['unit_cost'],
            44950,
            "The cost of Rich Soil should be 44.950 after purchased twice."
        )

    def test_02_TH3_product_avco_has_lot(self):
        """
            Product category has AVERAGE cost method
            Products:
                2 products has tracking number
                1 product  is None tracking

            A - Received 1 pothos at 1.000.000:
                => pothos_no_pot:        1.000.000 * 0.75 = 750.000
                => pot:                  1.000.000 * 0.15 = 150.000
                => soil:                 1.000.000 * 0.1  = 100.000
            B - Received 2 pothos at 800.000:
                => pothos_no_pot:        800.000 * 0.75 * 2 = 1.200.000
                => pot:                  800.000 * 0.15 * 2 = 240.000
                => soil:                 800.000 * 0.1  * 4 = 160.000
            D - Delivered 1 big_plant_pot: (has Tracking Number under Average Cost Method)
                => pot:                  -(240.000 / 2) = -130.000
                    Note: expected sale price = cost unit of product big_plant_pot
        """

        self.test_fifo_category.write({'property_cost_method': 'average'})
        self.pothos_plant_without_pot.write({'tracking': 'serial'})
        self.big_plant_pot.write({'tracking': 'serial'})
        self.soil_for_plant.write({'tracking': 'none'})

        # ========== TH3 - A ========== #

        purchase_order_line_1_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 1000000,
            }
        ]
        test_receipt_1 = self._create_confirm_order_and_validate_the_receipt('PO', purchase_order_line_1_data)
        res_1 = self._retrieve_inventory_valuation_layer_components(test_receipt_1)

        self.assertEqual(
            res_1[self.pothos_plant_without_pot.id]['value'],
            750000,
            "The cost of Pothos Plan Without Pot should be 750.000."
        )
        self.assertEqual(
            res_1[self.big_plant_pot.id]['value'],
            150000,
            "The cost of Big Plant Pot should be 150.000."
        )
        self.assertEqual(
            res_1[self.soil_for_plant.id]['value'],
            100000,
            "The cost of Rich Soil should be 100.000 for 2."
        )

        # ========== TH3 - B ========== #

        purchase_order_line_2_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 2,
                'product_uom': 1,
                'price_unit': 800000,
            }
        ]
        test_receipt_2 = self._create_confirm_order_and_validate_the_receipt('PO', purchase_order_line_2_data)
        res_2 = self._retrieve_inventory_valuation_layer_components(test_receipt_2)

        self.assertEqual(
            res_2[self.pothos_plant_without_pot.id]['unit_cost'],
            600000,
            "The unit cost of Pothos Plan Without Pot should be 600.000 after purchased twice."
        )
        self.assertEqual(
            res_2[self.big_plant_pot.id]['unit_cost'],
            120000,
            "The cost of Big Plant Pot should be 120.000 after purchased twice."
        )
        self.assertEqual(
            res_2[self.soil_for_plant.id]['unit_cost'],
            40000,
            "The cost of Rich Soil should be 40.000 after purchased twice."
        )
        self.assertEqual(
            res_1[self.pothos_plant_without_pot.id]['value'] + res_2[self.pothos_plant_without_pot.id]['value'],
            1950000,
            "The total value of all Pothos Plan Without Pot should be 750.000 + 1.200.000 = 1.950.000"
        )
        self.assertEqual(
            res_1[self.big_plant_pot.id]['value'] + res_2[self.big_plant_pot.id]['value'],
            390000,
            "The total value of all Big Plant Pot should be 150.000 + 240.000 = 390.000"
        )
        self.assertEqual(
            res_1[self.soil_for_plant.id]['value'] + res_2[self.soil_for_plant.id]['value'],
            260000,
            "The total value of all Rich Soil should be 100.000 + 160.000 = 260.000"
        )

        # ========== TH1 - C - Separated sale ========== #

        sales_order_line_list = [
            (0, 0, {
                'product_id': self.big_plant_pot.id,
                'product_uom_qty': 1,
            }),
        ]

        # get the Serial number from last time purchased product big_plant_pot
        pot_product = test_receipt_2.move_lines.filtered(lambda line: line.product_id.id == self.big_plant_pot.id)
        used_lot_plant_pot = pot_product.move_line_nosuggest_ids[0].lot_id

        test_order_3 = self._create_confirm_order_and_validate_the_receipt(
            input_order_type='SO',
            order_line_data_list=sales_order_line_list,
            get_receipt=False
        )
        test_receipt_3 = test_order_3.picking_ids[0]

        for move_line in test_receipt_3.move_ids_without_package:
            move_form = Form(move_line, view='stock.view_stock_move_operations')
            with move_form.move_line_ids.new() as line:
                line.lot_id = used_lot_plant_pot
            move_line = move_form.save()

        # Validate this receipt (Stock picking)
        test_receipt_3.button_validate()

        res_3 = self._retrieve_inventory_valuation_layer_components(test_receipt_3)
        self.assertEqual(
            res_3[self.big_plant_pot.id]['value'],
            -130000,
            "The cost of Pot Plant should be -130.000 for 1."
        )

    def test_02_TH4_purchase_product_standard_price(self):
        """
            Product category has Standard Price cost method
            All products are all None Tracking with standard price:
                pothos_plant_without_pot:    4
                big_plant_pot:               3
                soil:                        2

            A - Received 1 pothos at 1.000.000:
                                        value
                                        -----
                => pothos_no_pot:        4
                => pot:                  3
                => soil:                 2
        """

        self.test_fifo_category.write({'property_cost_method': 'standard'})
        self.pothos_plant_without_pot.write({'tracking': 'none', 'standard_price': 4})
        self.big_plant_pot.write({'tracking': 'none', 'standard_price': 3})
        self.soil_for_plant.write({'tracking': 'none', 'standard_price': 2})

        purchase_order_line_1_data = [
            {
                'product_id': self.pothos_office.id,
                'name': 'Order line Pothos Office 1',
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 10,
            }
        ]
        test_receipt_1 = self._create_confirm_order_and_validate_the_receipt('PO', purchase_order_line_1_data)
        res_1 = self._retrieve_inventory_valuation_layer_components(test_receipt_1)

        self.assertEqual(
            res_1[self.pothos_plant_without_pot.id]['value'],
            4,
            "The cost value of Pothos Plan Without Pot should be 4 according to its standard price."
        )
        self.assertEqual(
            res_1[self.big_plant_pot.id]['value'],
            3,
            "The total value of all Big Plant Pot should be 3 according to its standard price."
        )
        self.assertEqual(
            res_1[self.soil_for_plant.id]['value'],
            4,
            "The total value of all Rich Soil should be 4 for 2 according to its standard price."
        )
