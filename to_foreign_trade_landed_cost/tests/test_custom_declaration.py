from odoo import fields
from odoo.tests import tagged, Form
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError, UserError

from odoo.addons.to_foreign_trade.tests.common import TestCommon

@tagged('post_install', '-at_install')
class TestCustomDeclaration(TestCommon):
    
    def test_after_install_module_01(self):
        """
        [Functional Test] - TC01
        
        - Case: After install module, check created data
        - Expected Result:
            + There is a new journal, which created for landed cost . 
                And each company, which has chart of account setting up, will have default journal for landed cost.
        """
        # check created journal
        for company in self.env['res.company'].search([('chart_template_id', '!=', False)]):
            journal_id = self.env['account.journal'].search([('code', '=', 'ITLC'), ('company_id', '=', company.id)])
            self.assertTrue(len(journal_id) == 1)
            
    def test_create_company_01(self):
        """
        [Functional Test] - TC02
        
        - Case: Create new company, and set chart template for it
        - Expected Result:
            + created company has default journal for landed cost
        """
        new_company = self.env['res.company'].create({
            'name': 'Test New Company'
        })
        self.env.company.chart_template_id._load(15.0, 15.0, new_company)
        self.assertTrue(new_company.landed_cost_journal_id.code == 'ITLC')
            
    def test_confirm_export_custom_declaration_01(self):
        """
        [Functional Test] - TC03
        
        - Case: Confirm export custom declaration
        - Expected Result:
            + There is not new landed cost is created after confirming export custom declaration
        """
        # change tax group to not VAT
        self.tax_group_export_1.is_vat = False
        self.tax_group_export_2.is_vat = False
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        self.assertTrue(custom_declaration.landed_cost_count == 0)
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.landed_cost_count == 0)
        
        
    def test_confirm_import_custom_declaration_01(self):
        """
        [Functional Test] - TC04
        
        - Case: Confirm import custom declaration
        - Expected Result:
            + There is a new landed cost is created after confirming import custom declaration 
        *Note: Combine TC07, TC08 to check landed cost count
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.po1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        self.assertTrue(custom_declaration.landed_cost_count == 0)
        
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.landed_cost_count == 1)
        landed_cost = custom_declaration.landed_cost_ids[0]
        cost_lines = landed_cost.cost_lines
        adjustment_lines = landed_cost.valuation_adjustment_lines

        # check cost lines
        self.assertTrue(len(cost_lines) == 4)
        self.assertEqual(cost_lines.product_id, self.env.ref('to_foreign_trade_landed_cost.to_product_product_import_tax_cost'))
        product1_tax1_cost = cost_lines.filtered(lambda cl: 
                                                 self.import_product_1.name in cl.name and 
                                                 self.tax_import_1.name in cl.name and
                                                 float_compare(cl.price_unit, 35.42, 2) == 0 )
        product1_tax2_cost = cost_lines.filtered(lambda cl: 
                                                 self.import_product_1.name in cl.name and 
                                                 self.tax_import_2.name in cl.name and
                                                 float_compare(cl.price_unit, 19.48, 2) == 0 )
        product2_tax1_cost = cost_lines.filtered(lambda cl: 
                                                 self.import_product_2.name in cl.name and 
                                                 self.tax_import_1.name in cl.name and
                                                 float_compare(cl.price_unit, 637.56, 2) == 0 )
        product2_tax2_cost = cost_lines.filtered(lambda cl: 
                                                 self.import_product_2.name in cl.name and 
                                                 self.tax_import_2.name in cl.name and
                                                 float_compare(cl.price_unit, 350.66, 2) == 0 )
        self.assertTrue(len(product1_tax1_cost) == 1)
        self.assertTrue(len(product1_tax2_cost) == 1)
        self.assertTrue(len(product2_tax1_cost) == 1)
        self.assertTrue(len(product2_tax2_cost) == 1)
        
        # check adjustment lines
        self.assertTrue(len(adjustment_lines) == 4)
        product1_tax1_adjustment = adjustment_lines.filtered(lambda al: 
                                                 al.product_id == self.import_product_1 and
                                                 al.move_id == self.po1_stock_move1 and
                                                 float_compare(al.additional_landed_cost, 35.42, 2) == 0 )
        product1_tax2_adjustment = adjustment_lines.filtered(lambda al: 
                                                 al.product_id == self.import_product_1 and
                                                 al.move_id == self.po1_stock_move1 and
                                                 float_compare(al.additional_landed_cost, 19.48, 2) == 0 )
        product2_tax1_adjustment = adjustment_lines.filtered(lambda al: 
                                                 al.product_id == self.import_product_2 and
                                                 al.move_id == self.po1_stock_move2 and
                                                 float_compare(al.additional_landed_cost, 637.56, 2) == 0 )
        product2_tax2_adjustment = adjustment_lines.filtered(lambda al: 
                                                 al.product_id == self.import_product_2 and
                                                 al.move_id == self.po1_stock_move2 and
                                                 float_compare(al.additional_landed_cost, 350.66, 2) == 0 )
        self.assertTrue(len(product1_tax1_adjustment) == 1)
        self.assertTrue(len(product1_tax2_adjustment) == 1)
        self.assertTrue(len(product2_tax1_adjustment) == 1)
        self.assertTrue(len(product2_tax2_adjustment) == 1)
        
    def test_cancel_custom_declaration_02(self):
        """
        [Functional Test] - TC05
        
        - Case: Cancel import custom declaration, while its landed cost is posted
        - Expected Result:
            + Can't cancel custom declaration 
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.po1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        landed_cost = custom_declaration.landed_cost_ids[0]
        landed_cost.button_validate()
        with self.assertRaises(ValidationError):
            custom_declaration.action_cancel()
        
    def test_cancel_custom_declaration_04(self):
        """
        [Functional Test] - TC06
        
        - Case: Cancel import custom declaration, while its landed cost is not posted
        - Expected Result:
            + Can cancel custom declaration 
            + landed cost will be removed
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.po1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        custom_declaration.action_cancel()
        self.assertTrue(custom_declaration.state == 'cancel')
        self.assertTrue(custom_declaration.landed_cost_count == 0)
        
    def test_compute_landed_cost_01(self):
        """
        [Functional Test] - TC09
        
        - Case: Compute landed cost while it is created from custom declaration
        - Expected Result:
            + Can't compute
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.po1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        landed_cost = custom_declaration.landed_cost_ids[0]
        with self.assertRaises(UserError):
            landed_cost.compute_landed_cost()
            
    def test_validate_landed_cost_01(self):
        """
        [Functional Test] - TC10
        
        - Case: Validate landed cost while it is created from custom declaration, 
            and cost in cost lines is not consistent with cost in adjustment lines
        - Expected Result:
            + Can validate
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.po1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        landed_cost = custom_declaration.landed_cost_ids[0]
        cost_lines = landed_cost.cost_lines
        
        product1_tax1_cost = cost_lines.filtered(lambda cl: 
                                                 self.import_product_1.name in cl.name and 
                                                 self.tax_import_1.name in cl.name and
                                                 float_compare(cl.price_unit, 35.42, 2) == 0 )
        product1_tax1_cost[0].price_unit = 40.00
        landed_cost.button_validate()
        self.assertTrue(landed_cost.state == 'done')
