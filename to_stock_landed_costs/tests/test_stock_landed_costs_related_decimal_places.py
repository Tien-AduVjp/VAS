from odoo import tools
from odoo.tests import Form

from .common import TestStockLandedCostsCommonExtension


class TestLandedCostsReLatedDecimalPlaces(TestStockLandedCostsCommonExtension):
    """
        Note: method "compute_landed_costs" of Odoo has Round method with parameter as HAFT UP
        means:
            round down value from 1-4
            round up   value from 5-9
    """
    
    def setUp(self):
        super(TestLandedCostsReLatedDecimalPlaces, self).setUp()
        
        self.product_3 = self.env['product.product'].create({'name': 'Product to use 3', 'type': 'product', 'categ_id': self.category_product.id})
        
        # Temporary change - set rounding = 0.01 is equivalent to decimal places = 2
        self.env.company.currency_id.write({'rounding': 0.01})
    
    # -------------------------------------------------------------------------------------------------#
    # ------------------------------------------ HELPERS ----------------------------------------------#
    # -------------------------------------------------------------------------------------------------#
        
    def _create_landed_cost(self, split_method, price_unit, digits, test_receipt):
        """
            Create a landed cost order and compute the additional cost 
            :param: split_method [string] fx. 'equal', 'by_quantity', 'by_weight'
            :param: price_unit   [float]  fx. 99 or 99.9
        """
        
        # We need to round up the price_unit before passing it as value to the create function, because
        #    on the UI, if decimals of Product Price field = 1 and you fx. enter price = 9.75
        #    the Javascript will just the value according to the decimal places above
        #    before sending it to the server, aka. 9.8 will be sent instead of 9.75
        rounded_price_unit = tools.float_round(price_unit, precision_digits=digits)
        
        # Create a landed cost order
        with Form(self.env['stock.landed.cost']) as f:
            f.picking_ids.add(test_receipt)
            f.account_journal_id = self.expenses_journal
            
            with f.cost_lines.new() as fline:
                fline.product_id = self.product_service
                fline.split_method = split_method
                fline.price_unit = rounded_price_unit
            
            test_landed_cost = f.save()

        # Compute the landed cost using Compute button
        test_landed_cost.compute_landed_cost()

        # Check the computed landed costs
        computed_val_adj_lines = test_landed_cost.mapped('valuation_adjustment_lines')

        return computed_val_adj_lines.mapped('additional_landed_cost')

    def _create_order_and_receipt(self):
        """
            Create an order with order lines and validate it to get the receipt
        """
        
        test_order = self.env['purchase.order'].create({'partner_id': self.partner.id})
        order_line_data = [
            {
                'product_id': self.product_1.id,
                'order_id': test_order.id,
                'name': 'Order line data 1',
                'date_planned': test_order.date_order,   
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 200000,
            },
            {
                'product_id': self.product_2.id,
                'order_id': test_order.id,
                'name': 'Order line data 2',
                'date_planned': test_order.date_order,   
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 100000,
            },
            {
                'product_id': self.product_3.id,
                'order_id': test_order.id,
                'name': 'Order line data 3',
                'date_planned': test_order.date_order,   
                'product_qty': 1,
                'product_uom': 1,
                'price_unit': 150000,
            },
        ]
        self.env['purchase.order.line'].create(order_line_data)

        # Confirm this order
        test_order.button_confirm()

        # Receipt of this order - simulate the received receipt with "done" quantity
        test_receipt = test_order.picking_ids[0]
        self.move_lines_on_test_receipt = test_receipt.move_lines

        for move_line in self.move_lines_on_test_receipt:
            qty_done = move_line.quantity_done
            prod_uom_qty = move_line.product_uom_qty
            if qty_done != prod_uom_qty:
                move_line.write({'quantity_done': prod_uom_qty})

        # Validate this receipt (Stock picking)
        test_receipt.button_validate()
        
        return test_receipt
    
    # -------------------------------------------------------------------------------------------------#
    # ----------------------------------------- TEST CASES --------------------------------------------#
    # -------------------------------------------------------------------------------------------------#
        
    def test_03_decimal_currency_lesser_product_price(self):
        """
            Case test:
            
            Decimal Places of Currency:             2
            Decimal Places of Product Price:        3
            
            Test the extension of compute_landed_costs method
        """
        
        # Set decimal for Product Price
        self.env.ref('product.decimal_price').write({'digits': 3})
        
        test_receipt = self._create_order_and_receipt()
        
        # TH1
        actual_equal_split_landed_costs = self._create_landed_cost(
            split_method='equal', 
            price_unit=99.123, 
            digits=self.env.ref('product.decimal_price').digits,
            test_receipt=test_receipt
        )

        self.assertEqual(
            actual_equal_split_landed_costs, 
            [33.040, 33.040, 33.043], 
            ("Error: The landed costs has not been rounded correctly by using 'Equal' split method. " 
            "The result should be [33.030, 33.030, 33.034]")
        )
        
        # TH2
        actual_equal_split_landed_costs = self._create_landed_cost(
            split_method='equal', 
            price_unit=99.555,
            digits=self.env.ref('product.decimal_price').digits,
            test_receipt=test_receipt
        )

        self.assertEqual(
            actual_equal_split_landed_costs, 
            [33.190, 33.190, 33.175], 
            ("Error: The landed costs has not been rounded correctly by using 'Equal' split method. "
             "The result should be [33.190, 33.190, 33.175]")
        )
        
    def test_04_decimal_currency_greater_product_price(self):
        """
            Case test:
            
            Decimal Places of Currency:             2
            Decimal Places of Product Price:        1
            
            The value for landed costs will already be round right after you have just entered a cost value on this field
            
            Note that the rounding parameter of computing landed costs is HAFT UP,
                means 33.33 will be rounded up to 33.34
        """
        
        # Set decimal for Product Price
        self.env.ref('product.decimal_price').write({'digits': 1})
        
        test_receipt = self._create_order_and_receipt()
        
        # TH1
        actual_equal_split_landed_costs = self._create_landed_cost(
            split_method='equal', 
            price_unit=99.97,
            digits=self.env.ref('product.decimal_price').digits,
            test_receipt=test_receipt
        )
        
        self.assertEqual(
            actual_equal_split_landed_costs, 
            [33.4, 33.4, 33.2],
            ("Error: The landed costs has not been rounded correctly by using 'Equal' split method. "
             "The result should be [33.4, 33.4, 33.2]")
        )
        
        # TH2
        actual_equal_split_landed_costs = self._create_landed_cost(
            split_method='equal', 
            price_unit=99.39,
            digits=self.env.ref('product.decimal_price').digits,
            test_receipt=test_receipt,
        )
        
        self.assertEqual(
            actual_equal_split_landed_costs, 
            [33.2, 33.2, 33.0], 
            ("Error: The landed costs has not been rounded correctly by using 'Equal' split method. "
             "The result should be [33.2, 33.2, 33.0]")
        )
        
        # TH3
        actual_equal_split_landed_costs = self._create_landed_cost(
            split_method='equal', 
            price_unit=99.05,
            digits=self.env.ref('product.decimal_price').digits,
            test_receipt=test_receipt,
        )
        
        self.assertEqual(
            actual_equal_split_landed_costs, 
            [33.1, 33.1, 32.9], 
            ("Error: The landed costs has not been rounded correctly by using 'Equal' split method. "
             "The result should be [33.1, 33.1, 32.9]")
        )
        
        # TH4
        actual_equal_split_landed_costs = self._create_landed_cost(
            split_method='equal', 
            price_unit=99.04,
            digits=self.env.ref('product.decimal_price').digits,
            test_receipt=test_receipt,
        )
        
        self.assertEqual(
            actual_equal_split_landed_costs, 
            [33.0, 33.0, 33.0], 
            ("Error: The landed costs has not been rounded correctly by using 'Equal' split method. "
             "The result should be [33.0, 33.0, 33.0]")
        )
