from odoo.tests import Form, tagged
from odoo.exceptions import ValidationError

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestWarrantyClaim(TestBase):
    
    def test_compute_warranty_start_date_01(self):
        """
        [Form Test] - TC01
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.purchase_order_id = self.po1
            f.partner_id = self.partner
            self.assertEqual(f.warranty_start_date, self.po1.date_order.date())
            f.product_id = self.product
    
    def _compare_warranty_claim_policies_for_purchase(self, form_warranty_claim_policies, product, po):
        policies = po.order_line.filtered(lambda line: line.product_id == product).mapped('warranty_policy_ids')
        if len(form_warranty_claim_policies) == len(policies):
            set_form_policies = set()
            set_policies = set()
            for idx in range(len(form_warranty_claim_policies)):
                line = form_warranty_claim_policies.edit(idx)
                set_form_policies.add((line.product_milestone_id.id, line.apply_to))
            for policy in policies:
                set_policies.add((policy.product_milestone_id.id, policy.apply_to))
            return set_form_policies == set_policies
        else:
            return False
    
    def test_compute_warranty_claim_policy_ids_01(self):
        """
        [Form Test] - TC02
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.product_id = self.product2
            f.purchase_order_id = self.po1
            
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase(f.warranty_claim_policy_ids, f.product_id, f.purchase_order_id))
            self.assertTrue(f.partner_id == self.po1.partner_id)
            
    def test_compute_warranty_claim_policy_ids_02(self):
        """
        [Form Test] - TC03
        """
        # Add more warranty policy to product
        current_warranty_policy_vals = []
        for policy in self.product2.warranty_policy_ids:
            current_warranty_policy_vals.append((4, policy.id, 0))

        current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                                            'apply_to': 'purchase'}))
        self.product2.write({'warranty_policy_ids': current_warranty_policy_vals})
        
        # Create warranty claim for this product with its confirmed PO
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.product_id = self.product2
            f.purchase_order_id = self.po1
            
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase(f.warranty_claim_policy_ids, f.product_id, f.purchase_order_id))
            self.assertTrue(f.partner_id == self.po1.partner_id)
            
    def test_compute_warranty_claim_policy_ids_03(self):
        """
        [Form Test] - TC05
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.purchase_order_id = self.po1
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            f.product_id = self.product
            
    def test_compute_warranty_claim_policy_ids_04(self):
        """
        [Form Test] - TC06
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.product_id = self.product2
            f.purchase_order_id = self.po1
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase(f.warranty_claim_policy_ids, f.product_id, f.purchase_order_id))
            f.product_id = self.product
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase(f.warranty_claim_policy_ids, f.product_id, f.purchase_order_id))
    
    def test_compute_warranty_claim_policy_ids_05(self):
        """
        [Form Test] - TC07
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.product_id = self.product2
            f.purchase_order_id = self.po1
            self.assertTrue(self._compare_warranty_claim_policies_for_purchase(f.warranty_claim_policy_ids, f.product_id, f.purchase_order_id))
            f.product_id = self.product3
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            
    def _check_available_po_based_on_product(self, form_purchase_orders, product):
        
        purchase_orders = self.env['purchase.order']
        for po in form_purchase_orders:
            purchase_orders |= po
            
        if product:
            available_po = self.env['purchase.order'].search([('order_line.product_id', '=', product.id), ('state', 'in', ('purchase', 'done'))])
        else:
            available_po = self.env['purchase.order'].search([('state', 'in', ('purchase', 'done'))])
        self.assertTrue(available_po == purchase_orders)
            
    def test_compute_available_po_ids_01(self):
        """
        [Form Test] - TC08
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.product_id = self.product2
            self._check_available_po_based_on_product(f.available_po_ids, f.product_id)
            f.purchase_order_id = self.po1
            
    def test_compute_available_po_ids_02(self):
        """
        [Form Test] - TC08
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            self._check_available_po_based_on_product(f.available_po_ids, f.product_id)
            f.product_id = self.product2
            f.purchase_order_id = self.po1
            
    def test_action_investigation_01(self):
        """
        [Functional Test] - TC02
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'vendor'
        f.purchase_order_id = self.po2
        f.product_id = self.product2
        warranty_claim = f.save()
        with self.assertRaises(ValidationError):
            warranty_claim.action_investigation()
