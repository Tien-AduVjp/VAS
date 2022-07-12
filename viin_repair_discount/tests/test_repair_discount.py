from odoo.tests import TransactionCase, Form

class TestRepairDiscount(TransactionCase):
    def setUp(self):
        super().setUp()
        
        self.tax_id_15_percent = self.env.ref('l10n_generic_coa.1_sale_tax_template')

    def _create_invoice(self, repair_order, string_option):
        invoice = self.env['repair.advance.payment.inv'].create({
            'advance_payment_method': string_option
        })
        invoice.with_context({
            'active_id': repair_order.id,
            'active_ids': [repair_order.id]}
        ).create_invoices()

    def test_01_discount_on_repair_line(self):
        """
            Change discount on a repair line product.
    
            Input:
                Pick a repair order from demo data that includes:
                    repair line product
                        + price unit of 50.0
                        - no tax
                        - no discount
                    repair fee product
                        + price unit of 50.0
                        - no tax
                        - no discount
                put 15% tax on the product repair line
                put 10% discount on the product repair line
            Expect:
                After putting 15% tax:
                    The Subtotal         =  50.0 (at repair_line)
                    The tax amount       =   7.5 (at repair_order)
                    The untaxed amount   = 100.0 (at repair_order)
                    The total amount     = 107.5 (at repair_order)
                After putting 10% discount:
                    The Subtotal         =  45.0  (at repair_line)
                    The tax amount       =   6.75 (at repair_order)
                    The untaxed amount   =  95.0  (at repair_order)
                    The total amount     = 101.75 (at repair_order)
        """
    
        repair_order = self.env.ref('repair.repair_r2')
    
        self.assertTrue(bool(repair_order.fees_lines))
        self.assertTrue(bool(repair_order.operations))
    
        self.assertEqual(
            repair_order.operations[0].price_unit,
            50.0,
            "Price unit of repair line product should = 50.0"
        )
        self.assertEqual(
            repair_order.fees_lines[0].price_unit,
            50.0,
            "Price unit of repair fee product should = 50.0"
        )
    
        self.assertFalse(bool(repair_order.operations[0].tax_id))
        self.assertFalse(bool(repair_order.fees_lines[0].tax_id))
    
        self.assertEqual(repair_order.amount_tax, 0.0)
        self.assertEqual(repair_order.amount_untaxed, 100.0)
        self.assertEqual(repair_order.amount_total, 100.0)
    
        with Form(repair_order) as form:
            with form.operations.edit(0) as repair_line:
                repair_line.tax_id.add(self.tax_id_15_percent)
    
        self.assertTrue(bool(repair_order.operations[0].tax_id))
        self.assertEqual(repair_order.amount_tax, 7.5)
        self.assertEqual(repair_order.amount_untaxed, 100.0)
        self.assertEqual(repair_order.amount_total, 107.5)
    
        with Form(repair_order) as form:
            with form.operations.edit(0) as repair_line:
                repair_line.discount = 10
    
        self.assertEqual(repair_order.operations[0].discount, 10.0)
        self.assertEqual(repair_order.fees_lines[0].discount, 0.0)
    
        self.assertEqual(repair_order.operations[0].price_subtotal, 45)
        self.assertEqual(repair_order.fees_lines[0].price_subtotal, 50)
    
        self.assertEqual(repair_order.amount_tax, 6.75)
        self.assertEqual(repair_order.amount_untaxed, 50.0 + 45.0)
        self.assertEqual(repair_order.amount_total, 95.0 + 6.75)
    
    def test_02_discount_on_repair_fee(self):
        """
            Change discount on a repair fee product.
            Input:
                Pick a repair order from demo data that includes:
                    repair line product
                        + price unit of 50.0
                        - no tax
                        - no discount
                    repair fee product
                        + price unit of 50.0
                        - no tax
                        - no discount
                put 15% tax on the product repair fee
                put 10% discount on the product repair fee
            Expect:
                After putting 15% tax:
                    The Subtotal         =  50.0 (at repair_fee)
                    The tax amount       =   7.5 (at repair_order)
                    The untaxed amount   = 100.0 (at repair_order)
                    The total amount     = 107.5 (at repair_order)
                After putting 10% discount:
                    The Subtotal         =  45.0  (at repair_fee)
                    The tax amount       =  14.25 (at repair_order)
                    The untaxed amount   =  95.0  (at repair_order)
                    The total amount     = 109.25 (at repair_order)
        """
    
        repair_order = self.env.ref('repair.repair_r2')
    
        self.assertTrue(bool(repair_order.fees_lines))
        self.assertTrue(bool(repair_order.operations))
    
        self.assertEqual(
            repair_order.operations[0].price_unit,
            50.0,
            "Price unit of repair line product should = 50.0"
        )
        self.assertEqual(
            repair_order.fees_lines[0].price_unit,
            50.0,
            "Price unit of repair fee product should = 50.0"
        )
    
        self.assertFalse(bool(repair_order.operations[0].tax_id))
        self.assertFalse(bool(repair_order.fees_lines[0].tax_id))
    
        with Form(repair_order) as form:
            with form.fees_lines.edit(0) as repair_fee:
                repair_fee.tax_id.add(self.tax_id_15_percent)
    
        self.assertTrue(bool(repair_order.fees_lines[0].tax_id))
        self.assertEqual(repair_order.amount_tax, 7.5)
        self.assertEqual(repair_order.amount_untaxed, 100.0)
        self.assertEqual(repair_order.amount_total, 107.5)
    
        with Form(repair_order) as form:
            with form.fees_lines.edit(0) as repair_fee:
                repair_fee.discount = 10
    
        self.assertEqual(repair_order.operations[0].discount, 0.0)
        self.assertEqual(repair_order.fees_lines[0].discount, 10.0)
    
        self.assertEqual(repair_order.operations[0].price_subtotal, 50)
        self.assertEqual(repair_order.fees_lines[0].price_subtotal, 45)
    
        self.assertEqual(repair_order.amount_tax, 6.75)
        self.assertEqual(repair_order.amount_untaxed, 50.0 + 45.0)
        self.assertEqual(repair_order.amount_total, 95.0 + 6.75)

    def test_03_04_multi_discount_create_invoice(self):
        """
            Set discount on all repair line product and repair fee
    
            Input:
                1) Pick a repair order from demo data that includes:
                    repair line product
                        + price unit of 50.0
                        - no tax
                        - no discount
                    repair fee product
                        + price unit of 50.0
                        - no tax
                        - no discount
                2) Add 1 more repair fee => 2 repair fees in total
                    price unit set = 50.00
                3) put 15% tax on all the lines
                4) put 10% discount on all the lines
            Expect:
                with 15% tax and 10% discount on all the lines:
                    The unit price:
                        product repair line    = 50.0
                        old repair fee         = 50.0
                        new repair fee         = 50.0
                    The Subtotal:        
                        product repair line    = 50.0 * 10% = 45.0
                        old repair fee         = 50.0 * 10% = 45.0
                        new repair fee         = 50.0 * 10% = 45.0
                    The tax amount = 
                        45*15% + 45*15% + 45*15%            = 20.25
                    The untaxed amount =
                        45.0 + 45.0 + 45.0                  = 135.00
                    The total amount =
                        20.25 + 135.00                      = 155.25
        """
        product_price_decimal_places = self.env.ref('product.decimal_price').digits
        
        # Create repair order
        repair_order = self.env.ref('repair.repair_r2')

        self.assertEqual(len(repair_order.operations), 1)
        self.assertEqual(len(repair_order.fees_lines), 1)
        
        self.assertFalse(bool(repair_order.operations[0].tax_id))
        self.assertFalse(bool(repair_order.fees_lines[0].tax_id))
        
        # Create product repair line and repair fee
        with Form(repair_order) as form:
            with form.operations.edit(0) as repair_line:
                repair_line.tax_id.add(self.tax_id_15_percent)
                repair_line.discount = 10.0
            with form.fees_lines.edit(0) as repair_fee:
                repair_fee.tax_id.add(self.tax_id_15_percent)
                repair_fee.discount = 10.0
            with form.fees_lines.new() as new_repair_fee:
                new_repair_fee.product_id = self.env.ref('product.expense_hotel')
                new_repair_fee.price_unit = 50.0
                new_repair_fee.discount = 10.0
                new_repair_fee.tax_id.add(self.tax_id_15_percent)
        
        self.assertEqual(repair_order.operations[0].price_unit, 50.0)
        self.assertEqual(repair_order.fees_lines[0].price_unit, 50.0)
        self.assertEqual(repair_order.fees_lines[1].price_unit, 50.0)
        
        self.assertEqual(repair_order.operations[0].price_subtotal, 45.0)
        self.assertEqual(repair_order.fees_lines[0].price_subtotal, 45.0)
        self.assertEqual(repair_order.fees_lines[1].price_subtotal, 45.0)
        
        # Confirm to get the insufficient quantity
        if repair_order.state == 'draft':
            ro_res = repair_order.action_validate()
    
            if not isinstance(ro_res, bool):
                qty_repair_handler = self.env['stock.warn.insufficient.qty.repair'].create({
                    'repair_id': repair_order.id,
                    'product_id': repair_order.product_id.id,
                    'location_id': self.env.ref('stock.stock_location_14').id
                })
                qty_repair_handler.action_done()

        # ro = repair_order
        
        # 45.0*15% + 45.0*15% + 45.0*15% = 45.0 * 3 * 15% = 20.25
        ro_calc_amount_tax = 45.0 * 3 * (15/100)
        ro_amount_tax = round(ro_calc_amount_tax, product_price_decimal_places)
        
        # = 135.00
        ro_calc_amount_untaxed = 45.0 + 45.0 + 45.0
        ro_amount_untaxed = round(ro_calc_amount_untaxed, product_price_decimal_places)
        
        ro_calc_amount_total = ro_calc_amount_tax + ro_calc_amount_untaxed
        ro_amount_total = round(ro_calc_amount_total, product_price_decimal_places)
        
        self.assertEqual(repair_order.amount_tax, ro_amount_tax)
        self.assertEqual(repair_order.amount_untaxed, ro_amount_untaxed)
        self.assertEqual(repair_order.amount_total, ro_amount_total)
        
        # Create invoice
        repair_order.action_repair_invoice_create()
         
        invoice = repair_order.invoice_id
        
        self.assertEqual(invoice.amount_tax, ro_amount_tax)
        self.assertEqual(invoice.amount_tax_signed, ro_amount_tax)
        self.assertEqual(invoice.amount_total, ro_amount_total)
        self.assertEqual(invoice.amount_total_signed, ro_amount_total)
        self.assertEqual(invoice.amount_untaxed, ro_amount_untaxed)
        self.assertEqual(invoice.amount_untaxed_signed, ro_amount_untaxed)
