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
            f.type = 'customer'
            f.sale_order_id = self.so1
            f.partner_id = self.customer
            self.assertEqual(f.warranty_start_date, self.so1.date_order.date())
            f.product_id = self.product
    
    def _compare_warranty_claim_policies_for_sale(self, form_warranty_claim_policies, product, so):
        policies = so.order_line.filtered(lambda line: line.product_id == product).mapped('warranty_policy_ids')
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
            f.type = 'customer'
            f.product_id = self.product2
            f.sale_order_id = self.so1
            
            self.assertTrue(self._compare_warranty_claim_policies_for_sale(f.warranty_claim_policy_ids, f.product_id, f.sale_order_id))
            self.assertTrue(f.partner_id == self.so1.partner_id)
            
    def test_compute_warranty_claim_policy_ids_02(self):
        """
        [Form Test] - TC03
        """
        # Add more warranty policy to product
        current_warranty_policy_vals = []
        for policy in self.product2.warranty_policy_ids:
            current_warranty_policy_vals.append((4, policy.id, 0))

        current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                                            'apply_to': 'sale'}))
        self.product2.write({'warranty_policy_ids': current_warranty_policy_vals})
        
        # Create warranty claim for this product with its confirmed PO
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.product_id = self.product2
            f.sale_order_id = self.so1
            
            self.assertTrue(self._compare_warranty_claim_policies_for_sale(f.warranty_claim_policy_ids, f.product_id, f.sale_order_id))
            self.assertTrue(f.partner_id == self.so1.partner_id)
            
    def test_compute_warranty_claim_policy_ids_03(self):
        """
        [Form Test] - TC05
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.sale_order_id = self.so1
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            f.product_id = self.product
            
    def test_compute_warranty_claim_policy_ids_04(self):
        """
        [Form Test] - TC06
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.product_id = self.product2
            f.sale_order_id = self.so1
            self.assertTrue(self._compare_warranty_claim_policies_for_sale(f.warranty_claim_policy_ids, f.product_id, f.sale_order_id))
            f.product_id = self.product
            self.assertTrue(self._compare_warranty_claim_policies_for_sale(f.warranty_claim_policy_ids, f.product_id, f.sale_order_id))
    
    def test_compute_warranty_claim_policy_ids_05(self):
        """
        [Form Test] - TC07
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.product_id = self.product2
            f.sale_order_id = self.so1
            self.assertTrue(self._compare_warranty_claim_policies_for_sale(f.warranty_claim_policy_ids, f.product_id, f.sale_order_id))
            f.product_id = self.product3
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            
    def _check_available_so_based_on_product(self, form_sale_orders, product):
        
        sale_orders = self.env['sale.order']
        for so in form_sale_orders:
            sale_orders |= so
            
        if product:
            available_so = self.env['sale.order'].search([('order_line.product_id', '=', product.id), ('state', 'in', ('sale', 'done'))])
        else:
            available_so = self.env['sale.order'].search([('state', 'in', ('sale', 'done'))])
        self.assertTrue(available_so == sale_orders)
            
    def test_compute_available_so_ids_01(self):
        """
        [Form Test] - TC08
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.product_id = self.product2
            self._check_available_so_based_on_product(f.available_so_ids, f.product_id)
            f.sale_order_id = self.so1
            
    def test_compute_available_so_ids_02(self):
        """
        [Form Test] - TC08
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            self._check_available_so_based_on_product(f.available_so_ids, f.product_id)
            f.product_id = self.product2
            f.sale_order_id = self.so1
            
    def test_action_investigation_01(self):
        """
        [Functional Test] - TC02
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'customer'
        f.sale_order_id = self.so2
        f.product_id = self.product2
        warranty_claim = f.save()
        with self.assertRaises(ValidationError):
            warranty_claim.action_investigation()
