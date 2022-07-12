from odoo.tests import TransactionCase


class TestInventoryAdjustmentWithUnitCost(TransactionCase):

    def setUp(self):
        super().setUp()

        self.test_adjustment = self.env.ref('stock.stock_inventory_icecream')
        
        # cost method: standard
        # standard price: 70
        self.product = self.test_adjustment.product_ids[0]

    def test_01(self):
        """
            Standard price
        """
        self.assertEqual(self.product.cost_method, 'standard')
        self.test_adjustment.action_start()

        # Demo data
        adjustment_line_1 = self.test_adjustment.line_ids.filtered(lambda l: l.product_qty == 50)
        adjustment_line_2 = self.test_adjustment.line_ids.filtered(lambda l: l.product_qty == 40)        

        adjustment_line_1.write({'cost_price': 55})
        adjustment_line_2.write({'cost_price': 45})
        
        self.test_adjustment.action_validate()
        
        self.assertEqual(self.product.qty_available, 90)
        
        stock_quant_line_1 = self.product.stock_quant_ids.filtered(
            lambda st: st.lot_id == adjustment_line_1.prod_lot_id and st.quantity == 50)
        stock_quant_line_2 = self.product.stock_quant_ids.filtered(
            lambda st: st.lot_id == adjustment_line_2.prod_lot_id and st.quantity == 40)
        
        self.assertRecordValues(stock_quant_line_1, [{'quantity': 50, 'value': 3500}])
        self.assertRecordValues(stock_quant_line_2, [{'quantity': 40, 'value': 2800}])
        
        # Edit on stock quant
        stock_quant_line_1.with_context(inventory_mode=True).write({'quantity': 51, 'price_unit': 5555})
        
        self.assertRecordValues(stock_quant_line_1, [{'quantity': 51, 'value': 3570}])
        
    def test_02(self):
        """
            FIFO cost method
        """
        
        fifo_categ = self.env['product.category'].create({
            'name': 'FIFO CATEGORY',
            'property_cost_method': 'fifo',
        })
        
        self.product.categ_id = fifo_categ.id
        self.assertEqual(self.product.cost_method, 'fifo')
        
        self.test_adjustment.action_start()   

        adjustment_line_1 = self.test_adjustment.line_ids[0]
        adjustment_line_2 = self.test_adjustment.line_ids[1]

        adjustment_line_1.write({'product_qty': 2, 'cost_price': 100})
        adjustment_line_2.write({'product_qty': 4, 'cost_price': 150})

        self.test_adjustment.action_validate()
        
        self.assertEqual(self.product.qty_available, 6)
        
        stock_quant_line_1 = self.product.stock_quant_ids.filtered(
            lambda st: st.lot_id == adjustment_line_1.prod_lot_id and st.quantity == 2)
        stock_quant_line_2 = self.product.stock_quant_ids.filtered(
            lambda st: st.lot_id == adjustment_line_2.prod_lot_id and st.quantity == 4)
        
        # average cost = (2*200 + 4*100) / 6 = 133.33
        self.assertRecordValues(stock_quant_line_1, [{'quantity': 2, 'value': 266.67}])
        self.assertRecordValues(stock_quant_line_2, [{'quantity': 4, 'value': 533.33}])
        
        # Edit on stock quant
        stock_quant_line_1.with_context(inventory_mode=True).write({'inventory_quantity': 4, 'price_unit': 200})
        
        # Calculation:
        #    Already has 'quantity_svl' = 6 and 'value_svl' = 800 
        #    ==> 2*100 + 4*150 + 2*200 / 2 + 4 +2 = 800 + 400 / 8 = 1200 / 8 = 150
        #    So:
        #        150 * 4 = 600
        self.assertRecordValues(stock_quant_line_1, [{'quantity': 4, 'value': 600}])
        
    def test_03(self):
        """
            AVCO cost method
        """
        avco_categ = self.env['product.category'].create({
            'name': 'AVCO CATEGORY',
            'property_cost_method': 'average',
        })

        self.product.categ_id = avco_categ.id
        self.assertEqual(self.product.cost_method, 'average')
        
        self.test_adjustment.action_start()   

        adjustment_line_1 = self.test_adjustment.line_ids[0]
        adjustment_line_2 = self.test_adjustment.line_ids[1]        

        adjustment_line_1.write({'product_qty': 2, 'cost_price': 200})
        adjustment_line_2.write({'product_qty': 4, 'cost_price': 100})

        self.test_adjustment.action_validate()
        
        self.assertEqual(self.product.qty_available, 6)
        
        stock_quant_line_1 = self.product.stock_quant_ids.filtered(
            lambda st: st.lot_id == adjustment_line_1.prod_lot_id and st.quantity == 2)
        stock_quant_line_2 = self.product.stock_quant_ids.filtered(
            lambda st: st.lot_id == adjustment_line_2.prod_lot_id and st.quantity == 4)
        
        # average cost = (2*200 + 4*100) / 6 = 133.33
        self.assertRecordValues(stock_quant_line_1, [{'quantity': 2, 'value': 266.66}])
        self.assertRecordValues(stock_quant_line_2, [{'quantity': 4, 'value': 533.32}])
        
        # Edit on stock quant
        stock_quant_line_1.with_context(inventory_mode=True).write({'inventory_quantity': 4, 'price_unit': 200})
        
        # Calculation:
        #    Already has 'quantity_svl' = 6 and 'value_svl' = 800 
        #    ==> 2*100 + 4*150 + 2*200 / 2 + 4 +2 = 800 + 400 / 8 = 1200 / 8 = 150
        #    So:
        #        150 * 4 = 600
        self.assertRecordValues(stock_quant_line_1, [{'quantity': 4, 'value': 600}])
