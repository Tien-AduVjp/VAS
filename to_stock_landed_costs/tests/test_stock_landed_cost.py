from odoo.tests import tagged
from .common import TestStockLandedCostsCommonExtension


@tagged('post_install', '-at_install')
class TestStockLandedCostExtension(TestStockLandedCostsCommonExtension):
    """
        This scenario, we only need to test the case of currency with 0 decimal places, 
        because all currencies that has decimal places are already tested by Odoo by default
    """
    
    def setUp(self):
        super(TestStockLandedCostExtension, self).setUp()
        
        # Temporary change - set rounding = 1 is equivalent to decimal places = 0
        self.env.company.currency_id.write({'rounding': 1})
        
    def _create_landed_cost(self, split_method, price_unit):
        """
            Create a landed cost order and compute the additional cost 
            :param: split_method [string] fx. 'equal', 'by_quantity', 'by_weight'
            :param: price_unit   [float]  fx. 99 or 99.9
        """

        # Create a landed cost order
        self.test_landed_cost = self.env['stock.landed.cost'].create({
            'picking_ids': [(4, self.test_receipt.id)],
            'account_journal_id': self.expenses_journal.id,
            'cost_lines': [
                (0, 0, {'product_id': self.product_service.id, 'split_method': split_method, 'price_unit': price_unit}),
            ],
            'valuation_adjustment_lines': [],
        })

        # Compute the landed cost using Compute button
        self.test_landed_cost.compute_landed_cost()

        # Check the computed landed costs
        computed_val_adj_lines = self.test_landed_cost.mapped('valuation_adjustment_lines')

        return computed_val_adj_lines.mapped('additional_landed_cost') 

    # -------------------------------------------------------------------------------------------------#
    # ----------------------------------------- TEST CASES --------------------------------------------#
    # -------------------------------------------------------------------------------------------------#

    def test_01_round_up_currency_no_decimal_places(self):
        self.assertEqual(
            self.env.company.currency_id.decimal_places, 
            0, 
            "Error: This current currency is expected to be VND with 0 decimal places."
        )
       
        # Create an Purchase Order
        self.test_order = self.env['purchase.order'].create({'partner_id': self.partner.id})
        order_line_data = [
            {
                'product_id': self.product_1.id,
                'order_id': self.test_order.id,
                'name': 'Order line data 1',
                'date_planned': self.test_order.date_order,
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 200000,
            },
            {
                'product_id': self.product_2.id,
                'order_id': self.test_order.id,
                'name': 'Order line data 2',
                'date_planned': self.test_order.date_order,
                'product_qty': 4,
                'product_uom': 1,
                'price_unit': 100000,
            },
        ]
        self.test_order_lines = self.env['purchase.order.line'].create(order_line_data)

        # Confirm this order
        self.test_order.button_confirm()

        # Receipt of this order - simulate the received receipt with "done" quantity
        self.test_receipt = self.test_order.picking_ids[0]
        self.move_lines_on_test_receipt = self.test_receipt.move_lines

        for move_line in self.move_lines_on_test_receipt:
            qty_done = move_line.quantity_done
            prod_uom_qty = move_line.product_uom_qty
            if qty_done != prod_uom_qty:
                move_line.write({'quantity_done': prod_uom_qty})

        # Validate this receipt (Stock picking)
        self.test_receipt.button_validate()

        # On landed cost, add one Landed Cost service product and test with price unit as 99
        test_price_unit = 99

        # Test case EQUAL split method
        actual_equal_split_landed_costs = self._create_landed_cost(split_method='equal', price_unit=test_price_unit)

        self.assertNotEqual(
            actual_equal_split_landed_costs[0],
            actual_equal_split_landed_costs[1],
            "Error: The landed costs has not been rounded correctly by using 'Equal' split method and the currency has 0 decimal places."
        )

        # Test case EQUAL split method
        actual_quantity_split_landed_costs = self._create_landed_cost(split_method='by_quantity', price_unit=test_price_unit)

        total_quantity_of_order_lines = sum(self.test_order_lines.mapped('product_qty'))
        price_unit_per_one_receipt_line = test_price_unit / total_quantity_of_order_lines
        
        self.assertNotEqual(
            actual_quantity_split_landed_costs[0],
            price_unit_per_one_receipt_line,
            "Error: The landed costs has not been rounded correctly by using 'Quantity' split method and the currency has 0 decimal places."
        )
        
    def test_02_total_value_of_product_inventory_valuation_and_inventory_report_after_landed_costs_computed(self):
        self.assertEqual(
            self.env.company.currency_id.decimal_places,
            0,
            "Error: This current currency is expected to be VND with 0 decimal places."
        )
        
        # Create purchase order
        test_order = self.env['purchase.order'].create({'partner_id': self.partner.id})
        order_line_data = [
            {
                'product_id': self.product_with_serial.id,
                'order_id': test_order.id,
                'name': 'Order line Product with serial 1',
                'date_planned': test_order.date_order,
                'product_qty': 2,
                'product_uom': 1,
                'price_unit': 1000000,
                'taxes_id': False
            },
        ]
        self.test_order_lines = self.env['purchase.order.line'].create(order_line_data)
    
        # Confirm this order
        test_order.button_confirm()

        # Receipt of this order - simulate the received receipt with "done" quantity
        self.test_receipt = test_order.picking_ids[0]
        move_lines_on_test_receipt = self.test_receipt.move_line_ids_without_package

        # For further comparision
        lot_serial_list = []
        count = 1
        for move_line in move_lines_on_test_receipt:
            lot = '0000' + str(count)
            lot_serial_list.append(lot)
            move_line.write({'qty_done': move_line.product_uom_qty, 'lot_name': lot})
    
            count += 1
        
        # Validate this receipt (Stock picking)
        self.test_receipt.button_validate()
    
        test_price_unit = 6999999
    
        # Test landed cost:
        #    split_method      =    equal
        #    price_unit        =    6.999.999
        actual_quantity_split_landed_costs = self._create_landed_cost(split_method='equal', price_unit=test_price_unit)

        self.assertEqual(
            actual_quantity_split_landed_costs[0],
            test_price_unit,
            "Error: The landed costs has not been rounded correctly by using 'Quantity' split method and the currency has 0 decimal places."
        )
    
        # The cost will be updated in both Inventory Valuation and Inventory Report by hitting this button
        self.test_landed_cost.button_validate()
        
        # CHECK INVENTORY VALUATION (STOCK VALUATION LAYER)
        
        # I search the landed cost order in stock.landed.cost relation
        searched_landed_cost_order = self.env['stock.valuation.layer'].search([('stock_landed_cost_id', '=', self.test_landed_cost.id)]) 
        
        # ********************************
        #    We have:
        #        the landed cost        =        6.999.999
        #        the cost               =        2.000.000
        #                                       -----------
        #        Total valuation value  =        8.999.999
        the_landed_cost = searched_landed_cost_order.value
        the_cost = searched_landed_cost_order.stock_valuation_layer_id.value
        total_valuation_value = searched_landed_cost_order.stock_valuation_layer_id.remaining_value
        
        self.assertEqual(
            the_cost + the_landed_cost,
            total_valuation_value,
            "Error testing: sum of the cost and the landed cost should be equal to total value." 
        )
        self.assertEqual(total_valuation_value, 8999999, "Error testing: total value should be 8.999.999 VND.")
        
        # CHECK INVENTORY REPORT (STOCK.QUANT)
        
        product_related_lines = self.env['stock.quant'].search([ ('product_id.name', '=', 'Product with serial 1'), ('lot_id.name', 'in', lot_serial_list) ])
        total_report_value = sum(product_related_lines.mapped('value'))
        
        self.assertNotEqual(the_cost, total_report_value, "Error testing: landed cost has not been calculated for stock.quant. Product only has the cost.")
        self.assertNotEqual(total_valuation_value, total_report_value, "Error testing: total value in Inventory Report should be round up to 4.500.000 and is higher than the total value in Inventory Valuation.")
