from odoo import fields
from unittest.mock import patch

from odoo.tests import Form, tagged

from .common import TestCommon
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, ValidationError
from odoo.tools import mute_logger

@tagged('post_install', '-at_install')
class TestCustomDeclaraion(TestCommon):

    def _get_selected_pickings(self, form):
        selected_pickings = self.env['stock.picking']
        for pk in form.stock_picking_ids:
            selected_pickings |= pk
        return selected_pickings

    def _get_selected_so(self, form):
        selected_so = self.env['sale.order']
        for so in form.sale_order_ids:
            selected_so |= so
        return selected_so

    def _get_selected_po(self, form):
        selected_po = self.env['purchase.order']
        for po in form.purchase_order_ids:
            selected_po |= po
        return selected_po

    def _get_available_pickings(self, form):
        available_pickings = self.env['stock.picking']
        for pk in form.available_picking_ids:
            available_pickings |= pk
        return available_pickings

    def _get_available_invoices(self, form):
        available_invoices = self.env['account.move']
        for inv in form.available_invoice_ids:
            available_invoices |= inv
        return available_invoices

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
            f.sale_order_ids.add(self.so1)

            # check currency
            self.assertEqual(f.currency_id, self.so1.currency_id)

            # check currency rate
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)

            # check selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.so1_picking1 | self.so1_picking2))

            # check available pickings
            available_pickings = self._get_available_pickings(f)
            self.assertEqual(available_pickings, self.so1_picking1 | self.so1_picking2)

            # check invoices
            selected_so = self._get_selected_so(f)
            invoice_domain = [('partner_id', 'in', selected_so.partner_id.ids), ('move_type', '=', 'out_invoice')]
            expected_available_invoices = self.env['account.move'].search(invoice_domain)

            available_invoices = self._get_available_invoices(f)
            self.assertEqual(available_invoices, expected_available_invoices)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')

            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.so1_picking1 | self.so1_picking2))

            # remove selected sale order
            f.sale_order_ids.remove(id=self.so1.id)

            # check currency
            self.assertEqual(f.currency_id, self.env.company.currency_id)

            # check currency rate
            self.assertTrue(float_compare(f.currency_rate,1.0, 1) == 0)

            # check selected picking
            selected_pickings_after = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings_after) == 1)
            self.assertEqual(selected_pickings_after, selected_pickings)

            # check available pickings
            picking_domain = [('location_dest_id.is_custom_clearance', '=', True),
                              ('state', 'in', ['assigned', 'done']),
                              ('picking_type_id.code', '=', 'internal')]
            expected_available_pickings = self.env['stock.picking'].search(picking_domain)
            available_pickings = self._get_available_pickings(f)
            self.assertEqual(available_pickings, expected_available_pickings)

            # check invoices
            expected_available_invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice')])

            available_invoices = self._get_available_invoices(f)
            self.assertEqual(available_invoices, expected_available_invoices)

            # set again sale order because it is required for custom declaration
            f.sale_order_ids.add(self.so1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')

            # check selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.so1_picking1 | self.so1_picking2))

            f.stock_picking_ids.remove(id=selected_pickings[0].id)
            f.stock_picking_ids.add(self.so1_picking1)

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
                self.assertEqual(line.payment_term_id, self.env.company.export_tax_payment_term_id)
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
            f.stock_picking_ids.remove(id=self.so1_picking1.id)
            f.stock_picking_ids.add(self.so1_picking2)

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
                self.assertEqual(line.payment_term_id, self.env.company.export_tax_payment_term_id)
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
            f.purchase_order_ids.add(self.po1)

            # check currency
            self.assertEqual(f.currency_id, self.po1.currency_id)

            # check currency rate
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)

            # check selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))

            # check available pickings
            available_pickings = self._get_available_pickings(f)
            self.assertEqual(available_pickings, self.po1_picking1 | self.po1_picking2)

            # check invoices
            selected_po = self._get_selected_po(f)
            invoice_domain = [('partner_id', 'in', selected_po.partner_id.ids), ('move_type', '=', 'in_invoice')]
            expected_available_invoices = self.env['account.move'].search(invoice_domain)

            available_invoices = self._get_available_invoices(f)
            self.assertEqual(available_invoices, expected_available_invoices)

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
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')

            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))

            # remove selected sale order
            f.purchase_order_ids.remove(id=self.po1.id)

            # check currency
            self.assertEqual(f.currency_id, self.env.company.currency_id)

            # check currency rate
            self.assertTrue(float_compare(f.currency_rate,1.0, 1) == 0)

            # check selected picking
            selected_pickings_after = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings_after) == 1)
            self.assertEqual(selected_pickings_after, selected_pickings)

            # check available pickings
            picking_domain = [('location_dest_id.is_custom_clearance', '=', True),
                              ('state', 'in', ['assigned', 'done']),
                              ('picking_type_id.code', '=', 'incoming')]
            expected_available_pickings = self.env['stock.picking'].search(picking_domain)
            available_pickings = self._get_available_pickings(f)
            self.assertEqual(available_pickings, expected_available_pickings)

            # check invoices
            expected_available_invoices = self.env['account.move'].search([('move_type', '=', 'in_invoice')])

            available_invoices = self._get_available_invoices(f)
            self.assertEqual(available_invoices, expected_available_invoices)

            # set again sale order because it is required for custom declaration
            f.purchase_order_ids.add(self.po1)

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
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')

            # check selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))

            if selected_pickings != self.po1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking1)

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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
            f.stock_picking_ids.remove(id=self.po1_picking1.id)
            f.stock_picking_ids.add(self.po1_picking2)

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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)

            # change selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))

            if selected_pickings != self.po1_picking2:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking2)

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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)

            # change selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))

            if selected_pickings != self.po1_picking2:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)

            # change selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))
            if selected_pickings != self.po1_picking2:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking2)

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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)

            # change selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))
            if selected_pickings != self.po1_picking2:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking2)

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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            self.assertTrue(float_compare(f.currency_rate,1.540000, 6) == 0)

            # change selected picking
            selected_pickings = self._get_selected_pickings(f)
            self.assertTrue(len(selected_pickings) == 1)
            self.assertTrue(selected_pickings in (self.po1_picking1 | self.po1_picking2))
            if selected_pickings != self.po1_picking2:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking2)

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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
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
        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.import']) as f:
                    f.purchase_order_ids.add(po)
                    # expected purchase order and picking will be reset
                    selected_po = self._get_selected_po(f)
                    selected_pickings = self._get_selected_pickings(f)
                    self.assertEqual(selected_po, self.env['purchase.order'])
                    self.assertEqual(selected_pickings, self.env['stock.picking'])

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
        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.import']) as f:
                    f.purchase_order_ids.add(po)
                    # expected purchase order and picking will be reset
                    selected_po = self._get_selected_po(f)
                    selected_pickings = self._get_selected_pickings(f)
                    self.assertEqual(selected_po, self.env['purchase.order'])
                    self.assertEqual(selected_pickings, self.env['stock.picking'])

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
        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.export']) as f:
                    f.sale_order_ids.add(so)
                    # expected purchase order and picking will be reset
                    selected_so = self._get_selected_so(f)
                    selected_pickings = self._get_selected_pickings(f)
                    self.assertEqual(selected_so, self.env['sale.order'])
                    self.assertEqual(selected_pickings, self.env['stock.picking'])

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
        with mute_logger('odoo.tests.common.onchange'):
            with self.assertRaises(AssertionError):
                with Form(self.env['custom.declaration.export']) as f:
                    f.sale_order_id.add(so)
                    # expected purchase order and picking will be reset
                    selected_so = self._get_selected_so(f)
                    selected_pickings = self._get_selected_pickings(f)
                    self.assertEqual(selected_so, self.env['sale.order'])
                    self.assertEqual(selected_pickings, self.env['stock.picking'])\

    def test_check_tax_group_information_of_custom_declaration_01(self):
        """
        [Functional Test] - TC30

        - Case: Check tax group information of created custom declaration
        - Expected Result:
            + Tax group information of custom declaration will be generated after custom declaration is created
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)
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

        - Case: Check tax group information of edited custom declaration
        - Expected Result:
            + Tax group information of custom declaration will be generated after custom declaration is created
        """
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)
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
        with self.assertRaises(AssertionError):
            with Form(self.env['custom.declaration.import']) as f:
                with self.assertRaises(ValidationError):
                    f.purchase_order_ids.add(po)

    def test_open_custom_declaration_01(self):
        """
        [Functional Test] - TC33

        - Case: Open custom declaration which has selected picking is not done
        - Expected Result:
            + Can't open custom declaration
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
        so_picking = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)

        so_picking.button_validate()
        so_picking.action_confirm()
        so_picking.action_assign()

        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(so)
            f.request_date = fields.Date.from_string('2021-10-20')

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)
        custom_declaration1 = f.save()
        custom_declaration1.action_cancel()

        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
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
        po_picking._action_done()

        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_ids.add(po)
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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        custom_declaration.action_cancel()

        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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

        - Case: Create custom declaration which has SO and picking are not relevant (There are SO without selected picking)
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
                f.stock_picking_ids.add(self.so1_picking1)
                f.sale_order_ids.add(so)
                f.request_date = fields.Date.from_string('2021-10-20')

    def test_check_so_vd_picking_on_custom_declaration_02(self):
        """
        [Functional Test] - TC58-2

        - Case: Create custom declaration which has SO and picking are not relevant (There are pickings without selected SO)
        - Expected Result:
            + ValidationError occurs
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
        so_picking = so.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)

        so_picking.button_validate()
        so_picking.action_confirm()
        so_picking.action_assign()

        with self.assertRaises(ValidationError):
            with Form(self.env['custom.declaration.export']) as f:
                f.sale_order_ids.add(self.so1)
                f.sale_order_ids.add(so)
                f.request_date = fields.Date.from_string('2021-10-20')
                f.sale_order_ids.remove(id=so.id)

    def test_check_po_vd_picking_on_custom_declaration_01(self):
        """
        [Functional Test] - TC59

        - Case: Create custom declaration which has PO and picking are not relevant (There are PO without selected picking)
        - Expected Result:
            + Complete operation normally
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
                })]
        })
        po.button_confirm()

        with self.assertRaises(ValidationError):
            with Form(self.env['custom.declaration.import']) as f:
                f.stock_picking_ids.add(self.po1_picking1)
                f.purchase_order_ids.add(po)
                f.request_date = fields.Date.from_string('2021-10-20')
                f.stock_picking_ids.remove(id=self.po1_picking1.id)

    def test_check_po_vd_picking_on_custom_declaration_02(self):
        """
        [Functional Test] - TC59-2

        - Case: Create custom declaration which has PO and picking are not relevant (There are pickings without selected PO)
        - Expected Result:
            + Complete operation normally
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
                })]
        })
        po.button_confirm()

        with self.assertRaises(ValidationError):
            with Form(self.env['custom.declaration.import']) as f:
                f.purchase_order_ids.add(self.po1)
                f.purchase_order_ids.add(po)
                f.request_date = fields.Date.from_string('2021-10-20')
                f.purchase_order_ids.remove(id=po.id)

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
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.so1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.so1_picking1)

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
            + Complete operation normally
        """
        self.product_category_saleable.property_cost_method = 'average'
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.po1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking1)

        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_import_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 1043.12, 2) == 0)

        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_import_id': False})
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
            f.sale_order_ids.add(so)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            self.assertEqual(selected_pickings, so_picking)

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
        so_picking._action_done()
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
            f.purchase_order_ids.add(po)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            self.assertEqual(selected_pickings, po_picking)

        custom_declaration = f.save()

        stock_move1 = po_picking.move_lines.filtered(lambda ml: ml.product_id == self.import_product_1)[0]
        stock_move2 = po_picking.move_lines.filtered(lambda ml: ml.product_id == self.import_product_2)[0]

        po_picking.button_validate()
        po_picking.action_confirm()
        po_picking.action_assign()

        stock_move1.move_line_ids.write({'qty_done': 2.0})
        # set qty_done is less than expected to create backorders
        stock_move2.move_line_ids.write({'qty_done': 12.0})
        po_picking._action_done()
        with self.assertRaises(UserError):
            custom_declaration.action_open()

    def test_confirm_export_custom_declaration_01(self):
        """
        [Functional Test] - TC63

        - Case: Confirm export custom declaration
        - Expected Result:
            + There is not new landed cost is created after confirming export custom declaration
        """
        # change tax group to not VAT
        self.tax_group_export_1.is_vat = False
        self.tax_group_export_2.is_vat = False
        with Form(self.env['custom.declaration.export']) as f:
            f.sale_order_ids.add(self.so1)
            f.request_date = fields.Date.from_string('2021-10-20')

        custom_declaration = f.save()
        custom_declaration.action_open()
        self.assertTrue(custom_declaration.landed_cost_count == 0)
        custom_declaration.action_confirm()
        self.assertTrue(custom_declaration.landed_cost_count == 0)


    def test_confirm_import_custom_declaration_01(self):
        """
        [Functional Test] - TC64

        - Case: Confirm import custom declaration
        - Expected Result:
            + There is a new landed cost is created after confirming import custom declaration
        *Note: Combine TC07, TC08 to check landed cost count
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.po1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking1)

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
        self.assertEqual(cost_lines.product_id, self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost'))
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

    def test_cancel_custom_declaration_05(self):
        """
        [Functional Test] - TC65

        - Case: Cancel import custom declaration, while its landed cost is posted
        - Expected Result:
            + Can't cancel custom declaration
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')

        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        landed_cost = custom_declaration.landed_cost_ids[0]
        landed_cost.button_validate()
        with self.assertRaises(ValidationError):
            custom_declaration.action_cancel()

    def test_cancel_custom_declaration_06(self):
        """
        [Functional Test] - TC66

        - Case: Cancel import custom declaration, while its landed cost is not posted
        - Expected Result:
            + Can cancel custom declaration
            + landed cost will be removed
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')

        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        custom_declaration.action_cancel()
        self.assertTrue(custom_declaration.state == 'cancel')
        self.assertTrue(custom_declaration.landed_cost_count == 0)

    def test_compute_landed_cost_01(self):
        """
        [Functional Test] - TC67

        - Case: Compute landed cost while it is created from custom declaration
        - Expected Result:
            + Can't compute
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')

        custom_declaration = f.save()
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        landed_cost = custom_declaration.landed_cost_ids[0]
        with self.assertRaises(UserError):
            landed_cost.compute_landed_cost()

    def test_validate_landed_cost_01(self):
        """
        [Functional Test] - TC68

        - Case: Validate landed cost while it is created from custom declaration,
            and cost in cost lines is not consistent with cost in adjustment lines
        - Expected Result:
            + Can validate
        """
        # change tax group to not VAT
        self.tax_group_import_1.is_vat = False
        self.tax_group_import_2.is_vat = False
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_ids.add(self.po1)
            f.request_date = fields.Date.from_string('2021-10-20')
            selected_pickings = self._get_selected_pickings(f)
            if selected_pickings != self.po1_picking1:
                f.stock_picking_ids.remove(id=selected_pickings[0].id)
                f.stock_picking_ids.add(self.po1_picking1)

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

    def test_flow_of_custom_declaration_07(self):
        """
        [Functional Test] - TC71

        - Case: Create import custom declaration, which has multiple PO and pickings,
            then open, confirm and payment for it, combine to check split expense and landed cost
        - Expected Result:
            + Complete operation normally
        """
        self.tax_group_import_2.is_vat = False

        po2 = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_1.name,
                    'product_id': self.import_product_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 3.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })]
        })
        po2.button_confirm()
        po2_picking = po2.picking_ids[0]
        po2_stock_move1 = po2_picking.move_lines.filtered(lambda ml: ml.product_id == self.import_product_1)[0]

        po2_picking.button_validate()
        po2_picking.action_confirm()
        po2_picking.action_assign()

        po2_stock_move1.move_line_ids.write({'qty_done': 3.0})
        po2_picking._action_done()

        with Form(self.env['custom.declaration.import']) as f:
            f.stock_picking_ids.add(self.po1_picking1)
            f.purchase_order_ids.add(po2)
            selected_po = self._get_selected_po(f)
            selected_pickings = self._get_selected_pickings(f)
            self.assertEqual(selected_po, self.po1 | po2)
            self.assertEqual(selected_pickings, self.po1_picking1 | po2_picking)
            f.request_date = fields.Date.from_string('2021-10-20')

            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 3)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertTrue(line.product_id in (self.import_product_1 | self.import_product_2))
                if line.product_id == self.import_product_1 and line.stock_move_id.picking_id == self.po1_picking1:
                    self.assertEqual(line.product_uom, self.uom_unit)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                    self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 230.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 354.2, 2) == 0)
                elif line.product_id == self.import_product_1 and line.stock_move_id.picking_id == po2_picking:
                    self.assertEqual(line.product_uom, self.uom_unit)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                    self.assertTrue(float_compare(line.qty, 3.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 345.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 531.3, 2) == 0)
                else:
                    self.assertEqual(line.product_uom, self.uom_dozen)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_import_1 | self.tax_import_2)
                    self.assertTrue(float_compare(line.qty, 1.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 4140.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 6375.6, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 6)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.import_tax_payment_term_id)
                self.assertEqual(line.account_id, self.tax_paid_account)

                self.assertTrue(line.tax_id in self.tax_import_1 | self.tax_import_2)
                if line.product_id == self.import_product_1 and line.stock_move_id.picking_id == self.po1_picking1:
                    if line.tax_id == self.tax_import_1:
                        self.assertTrue(line.is_vat)
                        self.assertTrue(float_compare(line.amount, 35.42, 2) == 0)
                    else:
                        self.assertTrue(not line.is_vat)
                        self.assertTrue(float_compare(line.amount, 19.48, 2) == 0)
                elif line.product_id == self.import_product_1 and line.stock_move_id.picking_id == po2_picking:
                    if line.tax_id == self.tax_import_1:
                        self.assertTrue(line.is_vat)
                        self.assertTrue(float_compare(line.amount, 53.13, 2) == 0)
                    else:
                        self.assertTrue(not line.is_vat)
                        self.assertTrue(float_compare(line.amount, 29.22, 2) == 0)
                else:
                    if line.tax_id == self.tax_import_1:
                        self.assertTrue(line.is_vat)
                        self.assertTrue(float_compare(line.amount, 637.56, 2) == 0)
                    else:
                        self.assertTrue(not line.is_vat)
                        self.assertTrue(float_compare(line.amount, 350.66, 2) == 0)

        custom_declaration = f.save()

        # add expenses
        with Form(custom_declaration) as f:
            with f.extra_expense_ids.new() as expense1:
                available_products = self.env['product.product']
                for product in expense1.available_product_ids:
                    available_products |= product
                self.assertEqual(available_products, self.import_product_1 | self.import_product_2)
                expense1.product_id = self.expense_product_1
                expense1.expense_value = 120
                expense1.split_method = 'equal'
            with f.extra_expense_ids.new() as expense2:
                expense2.product_id = self.expense_product_2
                expense2.applied_product_ids.add(self.import_product_1)
                expense2.expense_value = 200
                expense2.split_method = 'by_quantity'
            with f.extra_expense_ids.new() as expense3:
                expense3.product_id = self.expense_product_3
                expense3.expense_value = 100
                expense3.split_method = 'by_cost'

        # split expenses:
        custom_declaration.button_split_extra_expenses()

        # check divided expenses on each declaration line
        for dec_line in custom_declaration.custom_declaration_line_ids:
            if dec_line.product_id == self.import_product_1 and dec_line.stock_move_id.picking_id == self.po1_picking1:
                self.assertTrue(float_compare(dec_line.extra_expense_currency, 124.88, 2) == 0)
                self.assertTrue(float_compare(dec_line.total_cost, 546.52, 2) == 0)
            elif dec_line.product_id == self.import_product_1 and dec_line.stock_move_id.picking_id == po2_picking:
                self.assertTrue(float_compare(dec_line.extra_expense_currency, 167.32, 2) == 0)
                self.assertTrue(float_compare(dec_line.total_cost, 788.97, 2) == 0)
            else:
                self.assertTrue(float_compare(dec_line.extra_expense_currency, 127.80, 2) == 0)
                self.assertTrue(float_compare(dec_line.total_cost, 6572.41, 2) == 0)

        for line in custom_declaration.tax_line_ids:
            if line.product_id == self.import_product_1 and line.stock_move_id.picking_id == self.po1_picking1:
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 54.65, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 30.06, 2) == 0)
            elif line.product_id == self.import_product_1 and line.stock_move_id.picking_id == po2_picking:
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 78.90, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 43.39, 2) == 0)
            else:
                if line.tax_id == self.tax_import_1:
                    self.assertTrue(float_compare(line.amount, 657.24, 2) == 0)
                else:
                    self.assertTrue(float_compare(line.amount, 361.48, 2) == 0)

        custom_declaration.action_open()

        self.assertTrue(custom_declaration.landed_cost_count == 0)

        custom_declaration.action_confirm()

        self.assertTrue(custom_declaration.landed_cost_count == 1)
        landed_cost = custom_declaration.landed_cost_ids[0]
        cost_lines = landed_cost.cost_lines
        adjustment_lines = landed_cost.valuation_adjustment_lines

        # check cost lines
        self.assertTrue(len(cost_lines) == 3)
        self.assertEqual(cost_lines.product_id, self.env.ref('viin_foreign_trade.to_product_product_import_tax_cost'))
        product1_tax2_cost_1 = cost_lines.filtered(lambda cl:
                                                 self.import_product_1.name in cl.name and
                                                 self.tax_import_2.name in cl.name and
                                                 float_compare(cl.price_unit, 30.06, 2) == 0 )
        product1_tax2_cost_2 = cost_lines.filtered(lambda cl:
                                                 self.import_product_1.name in cl.name and
                                                 self.tax_import_2.name in cl.name and
                                                 float_compare(cl.price_unit, 43.39, 2) == 0 )
        product2_tax2_cost = cost_lines.filtered(lambda cl:
                                                 self.import_product_2.name in cl.name and
                                                 self.tax_import_2.name in cl.name and
                                                 float_compare(cl.price_unit, 361.48, 2) == 0 )
        self.assertTrue(len(product1_tax2_cost_1) == 1)
        self.assertTrue(len(product1_tax2_cost_2) == 1)
        self.assertTrue(len(product2_tax2_cost) == 1)

        # check adjustment lines
        self.assertTrue(len(adjustment_lines) == 3)
        product1_tax2_adjustment_1 = adjustment_lines.filtered(lambda al:
                                                 al.product_id == self.import_product_1 and
                                                 al.move_id == self.po1_stock_move1 and
                                                 al.quantity == 2 and
                                                 float_compare(al.additional_landed_cost, 30.06, 2) == 0 )
        product1_tax2_adjustment_2 = adjustment_lines.filtered(lambda al:
                                                 al.product_id == self.import_product_1 and
                                                 al.move_id == po2_stock_move1 and
                                                 al.quantity == 3 and
                                                 float_compare(al.additional_landed_cost, 43.39, 2) == 0 )
        product2_tax2_adjustment = adjustment_lines.filtered(lambda al:
                                                 al.product_id == self.import_product_2 and
                                                 al.move_id == self.po1_stock_move2 and
                                                 al.quantity == 12 and
                                                 float_compare(al.additional_landed_cost, 361.48, 2) == 0 )
        self.assertTrue(len(product1_tax2_adjustment_1) == 1)
        self.assertTrue(len(product1_tax2_adjustment_2) == 1)
        self.assertTrue(len(product2_tax2_adjustment) == 1)


        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_import_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 1225.72, 2) == 0)

        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_import_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 7)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')

    def test_flow_of_custom_declaration_08(self):
        """
        [Functional Test] - TC72

        - Case: Create export custom declaration, which has multiple SO and pickings,
            then open, confirm and payment for it
        - Expected Result:
            + Complete operation normally
        """
        self.tax_group_export_2.is_vat = False
        self.env['stock.quant']._update_available_quantity(self.export_product_1, self.stock_location, 3)
        so2 = self.env['sale.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'partner_invoice_id': self.foreign_trade_partner.id,
            'partner_shipping_id': self.foreign_trade_partner.id,
            'pricelist_id': self.pricelist_eur.id,
            'order_line': [
                (0, 0, {
                    'name': self.export_product_1.name,
                    'product_id': self.export_product_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 100.0,
                    'tax_id': [(6, 0, [self.sale_tax.id])]
                })
            ],
        })
        so2.action_confirm()
        so2_picking = so2.picking_ids.filtered(lambda pk: pk.location_dest_id == self.checked_warehouse.exp_custom_zone_loc_id)
        so2_stock_move1 = so2_picking.move_lines.filtered(lambda ml: ml.product_id == self.export_product_1)[0]

        so2_picking.button_validate()
        so2_picking.action_confirm()
        so2_picking.action_assign()

        so2_stock_move1.move_line_ids.write({'qty_done': 3.0})
        so2_picking._action_done()

        with Form(self.env['custom.declaration.export']) as f:
            f.stock_picking_ids.add(self.so1_picking1)
            f.sale_order_ids.add(so2)
            selected_so = self._get_selected_so(f)
            selected_pickings = self._get_selected_pickings(f)
            self.assertEqual(selected_so, self.so1 | so2)
            self.assertEqual(selected_pickings, self.so1_picking1 | so2_picking)
            f.request_date = fields.Date.from_string('2021-10-20')

            # check custom declaration line
            self.assertTrue(len(f.custom_declaration_line_ids) == 3)
            for idx in range(len(f.custom_declaration_line_ids)):
                line = f.custom_declaration_line_ids.edit(idx)
                taxes = self.env['account.tax']
                for tax in line.tax_ids:
                    taxes |= tax
                self.assertTrue(line.product_id in (self.export_product_1 | self.export_product_2))
                if line.product_id == self.export_product_1 and line.stock_move_id.picking_id == self.so1_picking1:
                    self.assertEqual(line.product_uom, self.uom_unit)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_export_1 | self.tax_export_2)
                    self.assertTrue(float_compare(line.qty, 2.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 230.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 354.2, 2) == 0)
                elif line.product_id == self.export_product_1 and line.stock_move_id.picking_id == so2_picking:
                    self.assertEqual(line.product_uom, self.uom_unit)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_export_1 | self.tax_export_2)
                    self.assertTrue(float_compare(line.qty, 3.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 345.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 531.3, 2) == 0)
                else:
                    self.assertEqual(line.product_uom, self.uom_dozen)
                    self.assertEqual(line.currency_id, self.currency_eur)
                    self.assertEqual(taxes, self.tax_export_1 | self.tax_export_2)
                    self.assertTrue(float_compare(line.qty, 1.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost_currency, 2760.0, 2) == 0)
                    self.assertTrue(float_compare(line.total_cost, 4250.4, 2) == 0)

            # check tax line
            self.assertTrue(len(f.tax_line_ids) == 6)
            for idx in range(len(f.tax_line_ids)):
                line = f.tax_line_ids.edit(idx)
                self.assertEqual(line.payment_term_id, self.env.company.export_tax_payment_term_id)
                self.assertEqual(line.account_id, self.tax_paid_account)

                self.assertTrue(line.tax_id in self.tax_export_1 | self.tax_export_2)
                if line.product_id == self.export_product_1 and line.stock_move_id.picking_id == self.so1_picking1:
                    if line.tax_id == self.tax_export_1:
                        self.assertTrue(line.is_vat)
                        self.assertTrue(float_compare(line.amount, 35.42, 2) == 0)
                    else:
                        self.assertTrue(not line.is_vat)
                        self.assertTrue(float_compare(line.amount, 19.48, 2) == 0)
                elif line.product_id == self.export_product_1 and line.stock_move_id.picking_id == so2_picking:
                    if line.tax_id == self.tax_export_1:
                        self.assertTrue(line.is_vat)
                        self.assertTrue(float_compare(line.amount, 53.13, 2) == 0)
                    else:
                        self.assertTrue(not line.is_vat)
                        self.assertTrue(float_compare(line.amount, 29.22, 2) == 0)
                else:
                    if line.tax_id == self.tax_export_1:
                        self.assertTrue(float_compare(line.amount, 425.04, 2) == 0)
                    else:
                        self.assertTrue(float_compare(line.amount, 233.77, 2) == 0)

        custom_declaration = f.save()
        custom_declaration.action_open()

        self.assertTrue(custom_declaration.landed_cost_count == 0)

        custom_declaration.action_confirm()

        self.assertTrue(custom_declaration.landed_cost_count == 0)


        with Form(self.env['custom.declaration.payment'].with_context({
            'default_custom_dec_export_id': custom_declaration.id
        })) as payment_form:
            self.assertTrue(float_compare(payment_form.amount, 796.06, 2) == 0)

        wizard = payment_form.save()
        wizard = wizard.with_context({'default_custom_dec_export_id': False})
        wizard.action_pay()
        self.assertTrue(custom_declaration.account_moves_count == 7)
        self.assertTrue(custom_declaration.is_paid)
        self.assertTrue(custom_declaration.state == 'done')

    def test_flow_of_custom_declaration_09(self):
        """
        [Functional Test] - TC73

        - Case: Split expenses when custom declaration is already confirmed
        - Expected Result:
            + UserError occurs
        """

        with Form(self.env['custom.declaration.import']) as f:
            f.stock_picking_ids.add(self.po1_picking1)
            f.request_date = fields.Date.from_string('2021-10-20')

        custom_declaration = f.save()

        # add expenses
        with Form(custom_declaration) as f:
            with f.extra_expense_ids.new() as expense1:
                expense1.product_id = self.expense_product_1
                expense1.expense_value = 120
                expense1.split_method = 'equal'

        custom_declaration.action_open()
        custom_declaration.action_confirm()
        # split expenses:
        with self.assertRaises(UserError):
            custom_declaration.button_split_extra_expenses()
