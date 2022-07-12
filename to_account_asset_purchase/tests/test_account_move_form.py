from odoo.tests import common

from .asset_purchase_common import TestAssetPurchaseCommon


@common.tagged('post_install', '-at_install')
class TestAccountMoveForm(TestAssetPurchaseCommon):

    def test_01_change_auto_complete_on_customer_invoice(self):
        po = self._make_purchase_order(self.product_product, self.partner_a)
        self._create_invoice_from_po(po)

        move_form = common.Form(self.env['account.move'].with_context(default_move_type='out_invoice'))
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_product
            line_form.asset_category_id = self.asset_category
        move_form.purchase_vendor_bill_id = self.env['purchase.bill.union'].search([('partner_id', '=', self.partner_a.id)], limit=1)
        move = move_form.save()

        self.assertEqual(self.asset_category.asset_account_id,
                         move.invoice_line_ids.filtered(lambda l: l.asset_category_id).account_id)

    def test_02_change_auto_complete_on_vendor_invoice_with_stockrable(self):
        po = self._make_purchase_order(self.product_product, self.partner_a)
        self._create_invoice_from_po(po)

        move_form = common.Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_product
            line_form.asset_category_id = self.asset_category
        move_form.purchase_vendor_bill_id = self.env['purchase.bill.union'].search([('partner_id', '=', self.partner_a.id)], limit=1)
        move = move_form.save()

        self.assertEqual('product', self.product_product.type)
        self.assertEqual(self.product_product.property_account_expense_id or self.product_product.categ_id.property_account_expense_categ_id,
                         move.invoice_line_ids.filtered(lambda l: l.asset_category_id).account_id)

    def test_03_change_auto_complete_on_vendor_invoice_with_consumable(self):
        po = self._make_purchase_order(self.product_comsu, self.partner_b)
        self._create_invoice_from_po(po)

        move_form = common.Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_comsu
            line_form.asset_category_id = self.asset_category
        move_form.purchase_vendor_bill_id = self.env['purchase.bill.union'].search([('partner_id', '=', self.partner_b.id)], limit=1)
        move = move_form.save()

        self.assertEqual('consu', self.product_comsu.type)
        self.assertEqual(self.asset_category.asset_account_id,
                         move.invoice_line_ids.filtered(lambda l: l.asset_category_id).account_id)
