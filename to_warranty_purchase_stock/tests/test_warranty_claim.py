from odoo.tests import Form, tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestWarrantyClaim(TestBase):

    def _compare_warranty_claim_policies_for_purchase_stock(self, form_warranty_claim_policies, lot):
        policies = lot.warranty_claim_policy_ids.filtered(lambda wcp: wcp.apply_to == 'purchase')
        if len(form_warranty_claim_policies) == len(policies):
            set_form_policies = set()
            set_policies = set()
            for idx in range(len(form_warranty_claim_policies)):
                line = form_warranty_claim_policies.edit(idx)
                set_form_policies.add((line.product_milestone_id.id, line.apply_to, line.operation_start))
            for policy in policies:
                set_policies.add((policy.product_milestone_id.id, policy.apply_to, policy.operation_start))
            return set_form_policies == set_policies
        else:
            return False

    def _check_available_po_based_on_lot(self, form_purchase_orders, lot, product):

        purchase_orders = self.env['purchase.order']
        for po in form_purchase_orders:
            purchase_orders |= po

        if lot and lot.purchase_order_id:
            available_po = self.env['purchase.order'].search([('id', '=', lot.purchase_order_id.id), ('state', 'in', ('purchase', 'done'))])
        elif product:
            available_po = self.env['purchase.order'].search([('order_line.product_id', '=', product.id), ('state', 'in', ('purchase', 'done'))])
        else:
            available_po = self.env['purchase.order'].search([('state', 'in', ('purchase', 'done'))])
        self.assertTrue(available_po == purchase_orders)

    def test_compute_data_01(self):
        """
        [Form Test] - TC01
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.lot_id = self.lot1
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.purchase_order_id == self.po1)
            self.assertTrue(f.partner_id == self.vendor1)
            self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot1.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase_stock(f.warranty_claim_policy_ids, self.lot1))
            self._check_available_po_based_on_lot(f.available_po_ids, f.lot_id, f.product_id)

    def test_compute_data_02(self):
        """
        [Form Test] - TC02
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.lot_id = self.lot1
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.purchase_order_id == self.po1)
            self.assertTrue(f.partner_id == self.vendor1)
            self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot1.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase_stock(f.warranty_claim_policy_ids, self.lot1))
            self._check_available_po_based_on_lot(f.available_po_ids, f.lot_id, f.product_id)
            f.lot_id = self.env['stock.production.lot']
            self.assertTrue(not f.product_id)
            self.assertTrue(not f.purchase_order_id)
            self.assertTrue(not f.partner_id)
            self.assertTrue(not f.warranty_start_date)
            self.assertTrue(not f.warranty_period)
            self.assertTrue(not f.warranty_expiration_date)
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            self._check_available_po_based_on_lot(f.available_po_ids, f.lot_id, f.product_id)
            # Set lot again for some required fields
            f.lot_id = self.lot1

    def test_compute_data_03(self):
        """
        [Form Test] - TC03
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.lot_id = self.lot1
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.purchase_order_id == self.po1)
            self.assertTrue(f.partner_id == self.vendor1)
            self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot1.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase_stock(f.warranty_claim_policy_ids, self.lot1))
            self._check_available_po_based_on_lot(f.available_po_ids, f.lot_id, f.product_id)
            f.lot_id = self.lot2
            self.assertTrue(f.product_id == self.product_lot2)
            self.assertTrue(f.purchase_order_id == self.po2)
            self.assertTrue(f.partner_id == self.vendor2)
            self.assertTrue(f.warranty_start_date == self.lot2.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot2.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot2.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase_stock(f.warranty_claim_policy_ids, self.lot2))
            self._check_available_po_based_on_lot(f.available_po_ids, f.lot_id, f.product_id)
