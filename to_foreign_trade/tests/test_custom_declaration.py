from odoo import fields
from unittest.mock import patch

from odoo.tests import Form, tagged

from .common import TestCommon
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, ValidationError
from odoo.tools import mute_logger

@tagged('post_install', '-at_install')
class TestCustomDeclaraion(TestCommon):
    
    def test_change_so_on_export_custom_declaration_01(self):
        """
        [Form Test] - TC16
        
        - Case: Create export custom declaration, then select SO for it
        - Expected Result:
            + Currency on custom declaration will be set as currency on SO
            + Currency rate on custom declaration will set based on currency, request date and clearance date 
            + Selected picking will be one of pickings of SO
            + Available pickings are pickings of SO, which transfer product from WH to Custom Zone
            + Available invoices are account moves, which has partner is partner of SO
        """
        self.assertTrue(self.so1.foreign_trade)
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            
            # check currency
            self.assertEqual(f.currency_id, self.so1.currency_id)
            
            # check currency rate
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)
            
            # check selected picking
            self.assertTrue(f.stock_picking_id in (self.so1_picking1 | self.so1_picking2))
            
            # check available pickings
            pickings = self.env['stock.picking']
            for pk in f.available_picking_ids:
                pickings |= pk
            self.assertEqual(pickings, self.so1_picking1 | self.so1_picking2)
            
            # check invoices
            invoice_domain = [('partner_id', '=', f.sale_order_id.partner_id.id), ('type', '=', 'out_invoice')]
            available_invoices = self.env['account.move'].search(invoice_domain)
            
            invoices = self.env['account.move']
            for inv in f.available_invoice_ids:
                invoices |= inv
            self.assertEqual(invoices, available_invoices)
    
    
    def test_change_so_on_export_custom_declaration_02(self):
        """
        [Form Test] - TC17
        
        - Case: Create export custom declaration, select SO for it, then unselect SO
        - Expected Result:
            + Currency on custom declaration will be set as currency on current company
            + Currency rate on custom declaration will set based on currency, request date and clearance date 
            + Selected picking will be kept
            + Available pickings are pickings, which has state in [assigned, done], has destination location is custom zone
              and code is internal, not only belong to pickings of SO
            + Available invoices are all account moves
        """
        self.assertTrue(self.so1.foreign_trade)
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            
            picking = f.stock_picking_id
            
            # remove selected sale order
            f.sale_order_id = self.env['sale.order']
            
            # check currency
            self.assertEqual(f.currency_id, self.env.company.currency_id)
            
            # check currency rate
            
            self.assertTrue(float_compare(f.currency_rate,1.0, 1) == 0)
            
            # check selected picking
            self.assertEqual(f.stock_picking_id, picking)
            
            # check available pickings
            picking_domain = [('location_dest_id.is_custom_clearance', '=', True), 
                              ('state', 'in', ['assigned', 'done']),
                              ('picking_type_id.code', '=', 'internal')]
            available_pickings = self.env['stock.picking'].search(picking_domain)
            pickings = self.env['stock.picking']
            for pk in f.available_picking_ids:
                pickings |= pk
            self.assertEqual(pickings, available_pickings)
            
            # check invoices
            available_invoices = self.env['account.move'].search([('type', '=', 'out_invoice')])
            
            invoices = self.env['account.move']
            for inv in f.available_invoice_ids:
                invoices |= inv
            self.assertEqual(invoices, available_invoices)
            
            # set again sale order because it is required for custom declaration
            f.sale_order_id = self.so1
    

    def test_change_picking_on_export_custom_declaration_01(self):
        """
        [Form Test] - TC18
    
        - Case: Create export custom declaration, then select SO for it, then change selected picking
            + option on-fly tax computation is checked
        - Expected Result:
            + Custom declaration line will be updated based on selected picking
            + Tax line will be updated accordingly
        """
        self.assertTrue(self.so1.foreign_trade)
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            
            # check selected picking
            self.assertTrue(f.stock_picking_id in (self.so1_picking1 | self.so1_picking2))

            f.stock_picking_id = self.so1_picking1
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 2)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertTrue(line.product_id in (self.export_product_1 | self.export_product_2))
                if line.product_id == self.export_product_1:
                    self.assertEqual(line.product_uom, self.uom_unit)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_export_1 | self.tax_export_2)
                    self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 230.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 354.2, 2) == 0)
                else:
                    self.assertEqual(line.product_uom, self.uom_dozen)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_export_1 | self.tax_export_2)
                    self.assertTrue(float_compare(line.qty, 1.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 2760.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 4250.4, 2) == 0)
            
            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 4)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.export_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_export_1 | self.tax_export_2)
                if line.product_id == self.export_product_1:
                    if line.tax_id == self.tax_export_1:
                        self.assertTrue(float_compare(line.amount, 35.42, 2) == 0)
                    else:
                        self.assertTrue(float_compare(line.amount, 19.48, 2) == 0)
                else:
                    if line.tax_id == self.tax_export_1:
                        self.assertTrue(float_compare(line.amount, 425.04, 2) == 0)
                    else:
                        self.assertTrue(float_compare(line.amount, 233.77, 2) == 0)
                     
            
            # change selected picking
            f.stock_picking_id = self.so1_picking2
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.export_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_export_1 | self.tax_export_2)
                self.assertTrue(float_compare(line.qty, 1.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 2760.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 4250.4, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.export_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_export_1 | self.tax_export_2)
                if line.tax_id == self.tax_export_1:
                    self.assertTrue(float_compare(line.amount, 425.04, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 233.77, 2) == 0)
                    
    def test_change_po_on_import_custom_declaration_01(self):
        """
        [Form Test] - TC19
        
        - Case: Create import custom declaration, then select PO for it
        - Expected Result:
            + Currency on custom declaration will be set as currency on PO
            + Currency rate on custom declaration will set based on currency, request date and clearance date 
            + Selected picking will be one of pickings of PO
            + Available pickings are pickings of PO, which transfer product from Vendor to Custom Zone
            + Available invoices are account moves, which has partner is partner of PO
        """
        self.assertTrue(self.po1.foreign_trade)
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            
            # check currency
            self.assertEqual(f.currency_id, self.po1.currency_id)
            
            # check currency rate
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)
            
            # check selected picking
            self.assertTrue(f.stock_picking_id in (self.po1_picking1 | self.po1_picking2))
            
            # check available pickings
            pickings = self.env['stock.picking']
            for pk in f.available_picking_ids:
                pickings |= pk
            self.assertEqual(pickings, self.po1_picking1 | self.po1_picking2)
            
            # check invoices
            invoice_domain = [('partner_id', '=', f.purchase_order_id.partner_id.id), ('type', '=', 'in_invoice')]
            available_invoices = self.env['account.move'].search(invoice_domain)
            
            invoices = self.env['account.move']
            for inv in f.available_invoice_ids:
                invoices |= inv
            self.assertEqual(invoices, available_invoices)
    
    def test_change_po_on_import_custom_declaration_02(self):
        """
        [Form Test] - TC20
        
        - Case: Create import custom declaration, select PO for it, then unselect PO
        - Expected Result:
            + Currency on custom declaration will be set as currency on current company
            + Currency rate on custom declaration will set based on currency, request date and clearance date 
            + Selected picking will be kept
            + Available pickings are pickings, which has state in [assigned, done], has destination location is custom zone
              and code is incoming, not only belong to pickings of PO
            + Available invoices are all account moves
        """
        self.assertTrue(self.so1.foreign_trade)
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            
            picking = f.stock_picking_id
            
            # remove selected sale order
            f.purchase_order_id = self.env['purchase.order']
            
            # check currency
            self.assertEqual(f.currency_id, self.env.company.currency_id)
            
            # check currency rate
            
            self.assertTrue(float_compare(f.currency_rate,1.0, 1) == 0)
            
            # check selected picking
            self.assertEqual(f.stock_picking_id, picking)
            
            # check available pickings
            picking_domain = [('location_dest_id.is_custom_clearance', '=', True), 
                              ('state', 'in', ['assigned', 'done']),
                              ('picking_type_id.code', '=', 'incoming')]
            available_pickings = self.env['stock.picking'].search(picking_domain)
            pickings = self.env['stock.picking']
            for pk in f.available_picking_ids:
                pickings |= pk
            self.assertEqual(pickings, available_pickings)
            
            # check invoices
            available_invoices = self.env['account.move'].search([('type', '=', 'in_invoice')])
            
            invoices = self.env['account.move']
            for inv in f.available_invoice_ids:
                invoices |= inv
            self.assertEqual(invoices, available_invoices)
            
            # set again sale order because it is required for custom declaration
            f.purchase_order_id = self.po1

    def test_change_picking_on_import_custom_declaration_01(self):
        """
        [Form Test] - TC21
    
        - Case: Create import custom declaration, then select PO for it, then change selected picking
            + option on-fly tax computation is checked
        - Expected Result:
            + Custom declaration line will be updated based on selected picking
            + Tax line will be updated accordingly
        """
        self.assertTrue(self.po1.foreign_trade)
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            
            # check selected picking
            self.assertTrue(f.stock_picking_id in (self.po1_picking1 | self.po1_picking2))

            f.stock_picking_id = self.po1_picking1
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 2)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertTrue(line.product_id in (self.import_product_1 | self.import_product_2))
                if line.product_id == self.import_product_1:
                    self.assertEqual(line.product_uom, self.uom_unit)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                    self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 230.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 354.2, 2) == 0)
                else:
                    self.assertEqual(line.product_uom, self.uom_dozen)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                    self.assertTrue(float_compare(line.qty, 1.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 4140.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 6375.6, 2) == 0)
            
            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 4)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.product_id == self.import_product_1:
                    if line.tax_id == self.tax_import_1:
                        self.assertTrue(float_compare(line.amount, 35.42, 2) == 0)
                    else:
                        self.assertTrue(float_compare(line.amount, 19.48, 2) == 0)
                else:
                    if line.tax_id == self.tax_import_1:
                        self.assertTrue(float_compare(line.amount, 637.56, 2) == 0)
                    else:
                        self.assertTrue(float_compare(line.amount, 350.66, 2) == 0)
                     
            
            # change selected picking
            f.stock_picking_id = self.po1_picking2
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12751.2, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1275.12, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 701.32, 2) == 0)

    def test_change_request_date_on_custom_declaration_01(self):
        """
        [Form Test] - TC22
    
        - Case: Create import custom declaration, select PO and picking and request date, then change request date
            + option on-fly tax computation is checked
        - Expected Result:
            + Currency rate of custom declaration will be updated
            + Custom declaration line will be updated based on updated currency rate
            + Tax line will be updated accordingly
        """
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)
 
            # change selected picking
            f.stock_picking_id = self.po1_picking2
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12751.2, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1275.12, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 701.32, 2) == 0)
        
            f.request_date = fields.Date.from_string('2021-10-22')
            self.assertTrue(float_compare(f.currency_rate,1.500000, 6) == 0)
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12420.0, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1242.0, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 683.1, 2) == 0)

    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-10-22'))
    def test_change_request_date_on_custom_declaration_02(self):
        """
        [Form Test] - TC24
    
        - Case: Create import custom declaration, select PO and picking and request date, then remove request date
            + option on-fly tax computation is checked
        - Expected Result:
            + Currency rate of custom declaration will be updated
            + Custom declaration line will be updated based on updated currency rate
            + Tax line will be updated accordingly
        """
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)
              
            # change selected picking
            f.stock_picking_id = self.po1_picking2
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12751.2, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1275.12, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 701.32, 2) == 0)
        
            f.request_date = False
            self.assertTrue(float_compare(f.currency_rate,1.500000, 6) == 0)
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12420.0, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1242.0, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 683.1, 2) == 0)
                    
    def test_change_clearance_date_on_custom_declaration_01(self):
        """
        [Form Test] - TC23
    
        - Case: Create import custom declaration, select PO and picking and request date, then select clearance date
            + option on-fly tax computation is checked
        - Expected Result:
            + Currency rate of custom declaration will be updated
            + Custom declaration line will be updated based on updated currency rate
            + Tax line will be updated accordingly
        """
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)
            
            # change selected picking
            f.stock_picking_id = self.po1_picking2
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12751.2, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1275.12, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 701.32, 2) == 0)
        
            f.clearance_date = fields.Date.from_string('2021-10-22')
            self.assertTrue(float_compare(f.currency_rate,1.500000, 6) == 0)
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12420.0, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1242.0, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 683.1, 2) == 0)
                    
    def test_change_currency_rate_manual_01(self):
        """
        [Form Test] - TC25
    
        - Case: Create import custom declaration, select PO and picking and request date, then change currency rate
            + option on-fly tax computation is checked
        - Expected Result:
            + Currency rate of custom declaration will be updated
            + Custom declaration line will be updated based on updated currency rate
            + Tax line will be updated accordingly
        """
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)
            
            # change selected picking
            f.stock_picking_id = self.po1_picking2
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12751.2, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1275.12, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 701.32, 2) == 0)
        
            f.currency_rate = 1.500000
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12420.0, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1242.0, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 683.1, 2) == 0)
                    
    def test_change_currency_rate_manual_02(self):
        """
        [Form Test] - TC26
    
        - Case: Create import custom declaration, select PO and picking and request date, then change currency rate
            + option on-fly tax computation is not checked
        - Expected Result:
            + Currency rate of custom declaration will be updated
            + Custom declaration line will be updated based on updated currency rate
            + Tax line will not be updated
        """
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)
            
            # change selected picking
            f.stock_picking_id = self.po1_picking2
            
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12751.2, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1275.12, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 701.32, 2) == 0)
        
            f.compute_tax_lines_onfly = False
            f.currency_rate = 1.500000
            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 1)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertEqual(line.product_id, self.import_product_2)
                self.assertEqual(line.product_uom, self.uom_dozen)
                self.assertEqual(line.currency_id, self.currency_eur)
                self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost_currency, 8280.0, 2) == 0)
                self.assertTrue(float_compare(line.total_cost, 12420.0, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 2)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term)
                self.assertTrue(line.is_vat)
                self.assertEqual(line.account_id, self.tax_paid_account)
                self.assertTrue(line.tax_id, self.tax_import_1 | self.tax_import_2)
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 1275.12, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 701.32, 2) == 0)

    def test_create_custom_declaration_01(self):
        """
        [Functional Test] - TC26
        
        - Case: Create custom declaration which has selected PO and picking contains product has valuation is not automated
        - Expected Result:
            + Can't create custom declaration
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_not_real_time.name,
                    'product_id': self.import_product_not_real_time.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })
            ],
        })
        po.button_confirm()
        po_picking = po.picking_ids[0]
        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.import']) as f:
                    f.purchase_order_id = po
                    f.stock_picking_id = po_picking
                    # expected purchase order and picking will be reset
                    self.assertTrue(f.purchase_order_id, self.env['purchase.order'])
                    self.assertTrue(f.stock_picking_id, self.env['stock.picking'])
            
    def test_create_custom_declaration_02(self):
        """
        [Functional Test] - TC27
        
        - Case: Create custom declaration which has selected PO and picking contains product has cost method is not fifo
        - Expected Result:
            + Can't create custom declaration
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_not_fifo.name,
                    'product_id': self.import_product_not_fifo.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })
            ],
        })
        po.button_confirm()
        po_picking = po.picking_ids[0]
        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.import']) as f:
                    f.purchase_order_id = po
                    f.stock_picking_id = po_picking
                    # expected purchase order and picking will be reset
                    self.assertTrue(f.purchase_order_id, self.env['purchase.order'])
                    self.assertTrue(f.stock_picking_id, self.env['stock.picking'])
                
    def test_create_custom_declaration_03(self):
        """
        [Functional Test] - TC28
        
        - Case: Create custom declaration which has selected SO and picking contains product has valuation is not automated
        - Expected Result:
            + Can't create custom declaration
        """
        so = self.env['sale.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'partner_invoice_id': self.foreign_trade_partner.id,
            'partner_shipping_id': self.foreign_trade_partner.id,
            'pricelist_id': self.pricelist_eur.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_not_real_time.name,
                    'product_id': self.import_product_not_real_time.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                    'tax_id': [(6, 0, [self.sale_tax.id])]
                })]
        })
        so.action_confirm()
        so_picking = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)

        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.export']) as f:
                    f.sale_order_id = so
                    f.stock_picking_id = so_picking
                    # expected purchase order and picking will be reset
                    self.assertTrue(f.sale_order_id, self.env['sale.order'])
                    self.assertTrue(f.stock_picking_id, self.env['stock.picking'])
                
    def test_create_custom_declaration_04(self):
        """
        [Functional Test] - TC29
        
        - Case: Create custom declaration which has selected SO and picking contains product has cost method is not fifo
        - Expected Result:
            + Can't create custom declaration
        """
        so = self.env['sale.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'partner_invoice_id': self.foreign_trade_partner.id,
            'partner_shipping_id': self.foreign_trade_partner.id,
            'pricelist_id': self.pricelist_eur.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_not_fifo.name,
                    'product_id': self.import_product_not_fifo.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 100.0,
                    'tax_id': [(6, 0, [self.sale_tax.id])]
                })]
        })
        so.action_confirm()
        so_picking = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)

        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.export']) as f:
                    f.sale_order_id = so
                    f.stock_picking_id = so_picking
                    # expected purchase order and picking will be reset
                    self.assertTrue(f.sale_order_id, self.env['sale.order'])
                    self.assertTrue(f.stock_picking_id, self.env['stock.picking'])

    def test_check_tax_group_information_of_custom_declaration_01(self):
        """
        [Functional Test] - TC30
        
        - Case: Check tax group information of created custom declaration
        - Expected Result:
            + Tax group information of custom declaration will be generated after custom declaration is created
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        custom_declaration = f.save()
        self.assertTrue(len(custom_declaration.custom_dec_tax_group_ids) == 2)
        tax_groups = custom_declaration.custom_dec_tax_group_ids
        tax_group1 = tax_groups.filtered(lambda tg: tg.tax_group_id == self.tax_group_export_1)
        tax_group2 = tax_groups.filtered(lambda tg: tg.tax_group_id == self.tax_group_export_2)
        self.assertTrue(len(tax_group1) == 1)
        self.assertTrue(len(tax_group2) == 1)
        self.assertTrue(tax_group1[0].is_vat)
        self.assertTrue(tax_group2[0].is_vat)
        self.assertTrue(float_compare(tax_group1[0].amount, 460.46, 2) == 0)
        self.assertTrue(float_compare(tax_group2[0].amount, 253.25, 2) == 0)
        
    def test_check_tax_group_information_of_custom_declaration_02(self):
        """
        [Functional Test] - TC31
        
        - Case: Check tax group information of created custom declaration
        - Expected Result:
            + Tax group information of custom declaration will be generated after custom declaration is created
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        custom_declaration = f.save()
        
        with Form(custom_declaration) as f:
            f.currency_rate = 1.500000
        custom_declaration = f.save()
        
        self.assertTrue(len(custom_declaration.custom_dec_tax_group_ids) == 2)
        tax_groups = custom_declaration.custom_dec_tax_group_ids
        tax_group1 = tax_groups.filtered(lambda tg: tg.tax_group_id == self.tax_group_export_1)
        tax_group2 = tax_groups.filtered(lambda tg: tg.tax_group_id == self.tax_group_export_2)
        self.assertTrue(len(tax_group1) == 1)
        self.assertTrue(len(tax_group2) == 1)
        self.assertTrue(tax_group1[0].is_vat)
        self.assertTrue(tax_group2[0].is_vat)
        self.assertTrue(float_compare(tax_group1[0].amount, 448.50, 2) == 0)
        self.assertTrue(float_compare(tax_group2[0].amount, 246.68, 2) == 0)
        
    def test_tax_computation_01(self):
        """
        [Functional Test] - TC32
        
        - Case: Compute tax line of custom declaration in case import/export tax doesn't have account on their setting
        - Expected Result:
            + ValidationError occurs
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_abnormal_1.name,
                    'product_id': self.import_product_abnormal_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })]
        })
        po.button_confirm()
        po_picking = po.picking_ids[0]
        with self.assertRaises(AssertionError):
            with Form(self.env['custom.declaration.import']) as f:
                with self.assertRaises(ValidationError):
                    f.purchase_order_id = po
                    f.stock_picking_id = po_picking
        
    def test_open_custom_declaration_01(self):
        """
        [Functional Test] - TC33
        
        - Case: Open custom declaration which has selected picking is not done
        - Expected Result:
            + Can't open custom declaration
        """
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
        so_picking = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)

        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = so
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = so_picking
        
        custom_declaration = f.save()
        with self.assertRaises(UserError):
            custom_declaration.action_open()
            
    def test_open_custom_declaration_02(self):
        """
        [Functional Test] - TC34

        - Case: Open custom declaration successfully
        - Expected Result:
            + Custom declaration is opened
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
    
        custom_declaration = f.save()
        custom_declaration.action_open()
        self.assertTrue(custom_declaration.state == 'open')
        self.assertEqual(custom_declaration.request_date, fields.Date.from_string('2021-10-20'))
        
    def test_open_custom_declaration_03(self):
        """
        [Functional Test] - TC35

        - Case: Open custom declaration which has stock picking same with another custom declaration.
            + That custom declaration is not cancelled
        - Expected Result:
            + UserError occurs
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        
        custom_declaration2 = f.save()
        with self.assertRaises(UserError):
            custom_declaration2.action_open()
            
    def test_open_custom_declaration_04(self):
        """
        [Functional Test] - TC36

        - Case: Open custom declaration which has stock picking same with another custom declaration.
            + That custom declaration is cancelled
        - Expected Result:
            + Custom declaration is opened
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        custom_declaration1 = f.save()
        custom_declaration1.action_cancel()
        
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        
        custom_declaration2 = f.save()
        custom_declaration2.action_open()
        self.assertTrue(custom_declaration2.state == 'open')
        self.assertEqual(custom_declaration2.request_date, fields.Date.from_string('2021-10-20'))
        
    def test_confirm_custom_declaration_01(self):
        """
        [Functional Test] - TC38

        - Case: Confirm custom declaration which is not opened
        - Expected Result:
            + Custom declaration is not confirmed
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        custom_declaration = f.save()
        with self.assertRaises(UserError):
            custom_declaration.action_confirm()
            
    def test_confirm_custom_declaration_02(self):
        """
        [Functional Test] - TC39

        - Case: Confirm custom declaration which is has tax line has account is not allowed reconcile
        - Expected Result:
            + Custom declaration is not confirmed
        """
        self.tax_paid_account.reconcile = False
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        custom_declaration = f.save()
        custom_declaration.action_open()
        with self.assertRaises(ValidationError):
            custom_declaration.action_confirm()
    
    def test_confirm_custom_declaration_03(self):
        """
        [Functional Test] - TC39.2

        - Case: Confirm custom declaration which is has tax line has account, is VAT, but there is not VAT account
        - Expected Result:
            + Custom declaration is not confirmed
        """ 
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_abnormal_2.name,
                    'product_id': self.import_product_abnormal_2.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })]
        })
        po.button_confirm()
        po_picking = po.picking_ids[0]
        po_stock_move1 = po_picking.move_lines[0]
        po_picking.button_validate()
        po_picking.action_confirm()
        po_picking.action_assign()
        
        po_stock_move1.move_line_ids.write({'qty_done': 2.0})
        po_picking.action_done()
        
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = po
            f.stock_picking_id = po_picking
        custom_declaration = f.save()
        
        custom_declaration.action_open()
        with self.assertRaises(ValidationError):
            custom_declaration.action_confirm()
            
    def test_confirm_custom_declaration_04(self):
        """
        [Functional Test] - TC40

        - Case: Confirm custom declaration which has tax line has tax amount = 0
        - Expected Result:
            + There is not account move, which created for tax line has tax amount = 0
        """ 
        self.tax_export_2.amount = 0.0
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 2)
        
    def test_confirm_custom_declaration_05(self):
        """
        [Functional Test] - TC41

        - Case: Confirm custom declaration which has all tax lines has tax amount > 0
        - Expected Result:
            + There is new account move created for each tax line
        """ 
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 4)
        
    def test_payment_custom_declaration_01(self):
        """
        [Functional Test] - TC42

        - Case: Payment multiple times for custom declaration
        - Expected Result:
            + After each time of payment, amount need to payed will be reduced
            + After pay all required amount, custom declaration will be done
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 4)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            # payment less than required amount
            payment_form.amount = 413.71
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 5)
        self.assertTrue(not custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'confirm')
        
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 300.00, 2) == 0)
            # payment less than required amount
            payment_form.amount = 300.00
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 6)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')
    
    def test_payment_custom_declaration_02(self):
        """
        [Functional Test] - TC43

        - Case: Payment 1 time for custom declaration
        - Expected Result:
            + After pay required amount, custom declaration will be done
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 4)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 5)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')

    def test_payment_custom_declaration_03(self):
        """
        [Functional Test] - TC44

        - Case: Payment more than required amount
        - Expected Result:
            + ValidationError occurs
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 4)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            payment_form.amount = 714.00
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        with self.assertRaises(ValidationError):
            wizard.action_pay()
            
    def test_cancel_custom_declaration_01(self):
        """
        [Functional Test] - TC45

        - Case: Cancel custom declaration before confirming it
        - Expected Result:
            + Cancel successfully
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_cancel()
        self.assertTrue(custom_declaration.state == 'cancel')
        
    def test_cancel_custom_declaration_02(self):
        """
        [Functional Test] - TC46

        - Case: Cancel custom declaration after confirming it, but not yet payment
        - Expected Result:
            + Cancel successfully,
            + all account moves will be cancelled
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        custom_declaration.action_cancel()
        self.assertTrue(custom_declaration.account_moves_count == 4)
        self.assertTrue(custom_declaration.state == 'cancel')
        cancelled_account_moves = custom_declaration.account_move_ids.filtered(lambda am: am.state == 'cancel')
        self.assertEqual(cancelled_account_moves, custom_declaration.account_move_ids)
    
    def test_cancel_custom_declaration_03(self):
        """
        [Functional Test] - TC47

        - Case: Cancel custom declaration after confirming it, just payment a part 
        - Expected Result:
            + Cancel successfully,
            + all account moves will be cancelled
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 4)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            # payment less than required amount
            payment_form.amount = 413.71
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 5)
        self.assertTrue(not custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'confirm')
        custom_declaration.action_cancel()
        self.assertTrue(custom_declaration.state == 'cancel')
        cancelled_account_moves = custom_declaration.account_move_ids.filtered(lambda am: am.state == 'cancel')
        self.assertEqual(cancelled_account_moves, custom_declaration.account_move_ids)
        
    
    def test_cancel_custom_declaration_04(self):
        """
        [Functional Test] - TC48

        - Case: Cancel custom declaration after confirming it, already payment all 
        - Expected Result:
            + Cancel successfully,
            + all account moves will be cancelled
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 4)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 5)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')
        custom_declaration.action_cancel()
        self.assertTrue(custom_declaration.state == 'cancel')
        cancelled_account_moves = custom_declaration.account_move_ids.filtered(lambda am: am.state == 'cancel')
        self.assertEqual(cancelled_account_moves, custom_declaration.account_move_ids)
        
    def test_flow_of_custom_declaration_01(self):
        """
        [Functional Test] - TC51

        - Case: Cancel custom declaration after confirming it, then open again, confirm and payment
        - Expected Result:
            + Cancel successfully,
            + Open again, confirm and payment successfully
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        custom_declaration.action_cancel()
        custom_declaration.action_draft()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 8)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 9)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')
        
    def test_flow_of_custom_declaration_02(self):
        """
        [Functional Test] - TC52

        - Case: Cancel custom declaration after confirming it, then create the new one same with it, open confirm and payment
        - Expected Result:
            + Cancel successfully,
            + Create the new one, open, confirm and payment successfully
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        custom_declaration.action_cancel()
        
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        
        custom_declaration2 = f.save()
        custom_declaration2.action_open()
        custom_declaration2.action_confirm()
        self.assertTrue(custom_declaration2.account_moves_count == 4)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration2.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration2.account_moves_count == 5)
        self.assertTrue(custom_declaration2.is_paid)
        self.assertTrue(custom_declaration2.state == 'done')
        
    def test_flow_of_custom_declaration_03(self):
        """
        [Functional Test] - TC53

        - Case: Cancel custom declaration after done it, then open again, confirm and payment
        - Expected Result:
            + Cancel successfully,
            + Open again, confirm and payment successfully
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        
        custom_declaration.action_cancel()
        custom_declaration.action_draft()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.account_moves_count == 9)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 10)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')
        
    def test_flow_of_custom_declaration_04(self):
        """
        [Functional Test] - TC54

        - Case: Cancel custom declaration after done it, then create the new one same with it, open confirm and payment
        - Expected Result:
            + Cancel successfully,
            + Create the new one, open, confirm and payment successfully
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        
        custom_declaration.action_cancel()
        
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
        
        custom_declaration2 = f.save()
        custom_declaration2.action_open()
        custom_declaration2.action_confirm()
        self.assertTrue(custom_declaration2.account_moves_count == 4)
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration2.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration2.account_moves_count == 5)
        self.assertTrue(custom_declaration2.is_paid)
        self.assertTrue(custom_declaration2.state == 'done')
    
    def test_check_so_vd_picking_on_custom_declaration_01(self):
        """
        [Functional Test] - TC58
        
        - Case: Create custom declaration which has SO and picking are not relevant
        - Expected Result:
            + ValidationError occurs
        """
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
        
        with self.assertRaises(ValidationError):
            with Form(self.env['custom.declaration.export']) as f:
                f.sale_order_id = so
                f.request_date = fields.Date.from_string('2021-10-20')
                f.stock_picking_id = self.so1_picking1
                
    def test_check_po_vd_picking_on_custom_declaration_01(self):
        """
        [Functional Test] - TC59
        
        - Case: Create custom declaration which has PO and picking are not relevant
        - Expected Result:
            + Complete operation normally
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_abnormal_2.name,
                    'product_id': self.import_product_abnormal_2.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })]
        })
        po.button_confirm()
        
        with self.assertRaises(ValidationError):
            with Form(self.env['custom.declaration.import']) as f:
                f.purchase_order_id = po
                f.request_date = fields.Date.from_string('2021-10-20')
                f.stock_picking_id = self.po1_picking1
                
    def test_flow_of_custom_declaration_05(self):
        """
        [Functional Test] - TC60
        
        - Case: Create, open, confirm and payment for export custom declaration,
             which has picking contain products has cost method is average
        - Expected Result:
            + Complete operation normally
        """
        self.product_category_saleable.property_cost_method = 'average'
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = self.so1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.so1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 713.71, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 5)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')
        
    def test_flow_of_custom_declaration_06(self):
        """
        [Functional Test] - TC60
        
        - Case: Create, open, confirm and payment for import custom declaration,
             which has picking contain products has cost method is average
        - Expected Result:
            + ValidationError occurs
        """
        self.product_category_saleable.property_cost_method = 'average'
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = self.po1_picking1
            
        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_import_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 1043.12, 2) == 0)
            
        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 5)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')
        
    def test_check_consistency_between_picking_and_dec_lines_01(self):
        """
        [Functional Test] - TC61
        
        - Case: Open export custom declaration,
             which has picking is not consistent with declaration lines
        - Expected Result:
            + UserError occurs
        """
        self.env['stock.quant']._update_available_quantity(self.export_product_1, self.stock_location, 2)
        self.env['stock.quant']._update_available_quantity(self.export_product_2, self.stock_location, 24)
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
                }),
                (0, 0, {
                    'name': self.export_product_2.name,
                    'product_id': self.export_product_2.id,
                    'product_uom': self.uom_dozen.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 2400.0,
                    'tax_id': [(6, 0, [self.sale_tax.id])]
                })
            ],
        })
        so.action_confirm()
        so_picking = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)
        
        # create custom declaration
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_id = so
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = so_picking
            
        custom_declaration = f.save()
        
        # complete picking after creating custom declaration
        stock_move1 = so_picking.move_lines.filtered(lambda ml: ml.product_id == self.export_product_1)[0]
        stock_move2 = so_picking.move_lines.filtered(lambda ml: ml.product_id == self.export_product_2)[0]
        
        so_picking.button_validate()
        so_picking.action_confirm()
        so_picking.action_assign()
        
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        # set qty_done is less than expected to create backorders
        stock_move2.move_line_ids.write({'qty_done': 12.0})
        so_picking.action_done()
        with self.assertRaises(UserError):
            custom_declaration.action_open()
            
    def test_check_consistency_between_picking_and_dec_lines_02(self):
        """
        [Functional Test] - TC62
        
        - Case: Open import custom declaration,
             which has picking is not consistent with declaration lines
        - Expected Result:
            + UserError occurs
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_1.name,
                    'product_id': self.import_product_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                }),
                (0, 0, {
                    'name': self.import_product_2.name,
                    'product_id': self.import_product_2.id,
                    'product_uom': self.uom_dozen.id,
                    'product_qty': 3.0,
                    'price_unit': 3600.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })
            ],
        })
        po.button_confirm()
        po_picking = po.picking_ids[0]
        # create custom declaration
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = po
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = po_picking
            
        custom_declaration = f.save()
        
        stock_move1 = po_picking.move_lines.filtered(lambda ml: ml.product_id == self.import_product_1)[0]
        stock_move2 = po_picking.move_lines.filtered(lambda ml: ml.product_id == self.import_product_2)[0]
        
        po_picking.button_validate()
        po_picking.action_confirm()
        po_picking.action_assign()
        
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        # set qty_done is less than expected to create backorders
        stock_move2.move_line_ids.write({'qty_done': 12.0})
        po_picking.action_done()
        with self.assertRaises(UserError):
            custom_declaration.action_open()
