from odoo.tests import tagged
from odoo.exceptions import UserError

from .test_common import TestAffiliateCommon


@tagged('post_install', '-at_install')
class TestFlow(TestAffiliateCommon):

    def test_commission__order_draft(self):
        # Case: order state = draft link to affiliate code
        # Result: no commission was generated
        self.sale_order_1.affcode_id = self.aff_code_1.id
        self.assertEqual(self.sale_order_1.state, 'draft')
        self.assertEqual(self.sale_order_1.commission_ids_count, 0)

    def test_commission__order_confirm_01(self):
        # Case: confirm sale_order when no data about rules was found
        # Result: no commission was generated
        self.env['affiliate.commission.rule'].search([]).unlink()
        self.aff_code_1.commission_rule_ids = False
        self.aff_code_1.company_id = self.company_1.id
        self.sale_order_1.affcode_id = self.aff_code_1.id
        self.sale_order_1.action_confirm()
        self.assertEqual(self.sale_order_1.commission_ids_count, 0)

    def test_commission__order_confirm_02(self):
        # Case: confirm sale_order (affiliate code is not link to any rule)
        # Result: get the first rule satisfied for commission amount (6%)

        self.aff_code_1.write({
            'company_id': self.company_1.id,
            'commission_rule_ids': False
        })
        self.aff_code_1.flush()
        self.sale_order_1.action_confirm()
        self.assertEqual(self.sale_order_1.commission_ids_count, 1)
        self.assertEqual(self.sale_order_1.commission_ids.line_ids.affiliate_comm_percentage, 3)
        self.assertEqual(self.sale_order_1.commission_ids.comm_amount, 1350000)

    def test_commission_order_confirm_03(self):
        # Case: confirm sale_order using affiliate code has more than one rule
        # Result: get the first rule for computing commission amount (3%)
        self.aff_code_1.commission_rule_ids = [(6, 0, [self.commission_rule_product.id, self.commission_rule_category.id])]
        self.sale_order_1.action_confirm()
        self.assertEqual(self.sale_order_1.commission_ids_count, 1)
        self.assertEqual(self.sale_order_1.commission_ids.line_ids.affiliate_comm_percentage, self.commission_rule_product.line_ids.affiliate_comm_percentage)
        self.assertEqual(self.sale_order_1.commission_ids.comm_amount, 1350000)

        # Case: cancel sale order
        # Result: commission are also deleted
        self.sale_order_1.action_cancel()
        self.assertEqual(self.sale_order_1.commission_ids_count, 0)

    def test_commission_order_cancel_01(self):
        # Case: commission in state submit => cancel sale order
        # Result: Error
        self.aff_code_1.write({
            'commission_rule_ids': [(6, 0, [self.commission_rule_product.id, self.commission_rule_category.id])],
            'company_id': self.company_1.id
        })
        self.aff_code_1.flush()
        self.sale_order_1.action_confirm()
        self.assertEqual(self.sale_order_1.commission_ids_count, 1)
        self.payment_request.action_confirm()
        self.assertEqual(len(self.payment_request.com_ids), 1)
        self.assertEqual(self.payment_request.total, 1350000)
        self.assertEqual(self.sale_order_1.commission_ids.state, 'submit')
        with self.assertRaises(UserError):
            self.sale_order_1.action_cancel()

    def test_commission_order_cancel_02(self):
        # Case: commission in state comm_paid => cancel sale order
        # Result: Error
        self.aff_code_1.write({
            'commission_rule_ids': [(6, 0, [self.commission_rule_product.id, self.commission_rule_category.id])],
            'company_id': self.company_1.id
        })
        self.aff_code_1.flush()
        self.sale_order_1.action_confirm()
        self.payment_request.action_confirm()
        self.payment_request.action_approve()
        invoice = self.payment_request.invoice_ids
        invoice.action_invoice_paid()
        self.assertEqual(self.payment_request.state, 'paid')
        with self.assertRaises(UserError):
            self.sale_order_1.action_cancel()

    def test_affiliate__after_discount(self):
        # Case: setup compute method affiliate: before discount
        # Result: Commission Amount = (unit price * qty) * commission percentage / 100 (each sale order line)
        self.company_1.compute_aff_method = 'after_discount'
        self.aff_code_1.write({
            'commission_rule_ids': [(6, 0, [self.commission_rule_product.id, self.commission_rule_category.id])],
            'company_id': self.company_1.id
        })
        self.aff_code_1.flush()
        self.sale_order_1.order_line.discount = 5
        self.sale_order_1.action_confirm()
        self.assertEqual(self.sale_order_1.commission_ids.comm_amount, 1282500)

    def test_affiliate__before_discount(self):
        # Case: setup compute method affiliate: before discount
        # Result: commission amount = untaxed amount sale order * commission percentage / 100
        self.company_1.compute_aff_method = 'before_discount'
        self.aff_code_1.write({
            'commission_rule_ids': [(6, 0, [self.commission_rule_product.id, self.commission_rule_category.id])],
            'company_id': self.company_1.id
        })
        self.aff_code_1.flush()
        self.sale_order_1.action_confirm()
        self.assertEqual(self.sale_order_1.commission_ids.comm_amount, 1350000)
