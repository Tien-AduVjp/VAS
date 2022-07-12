from odoo.tests import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestRefund(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestRefund, cls).setUpClass()
        cls.pos_config = cls.env.ref('point_of_sale.pos_config_main')
        cls.partner_demo = cls.env.ref('base.partner_demo')
        cls.cash_payment_method = cls.env['pos.payment.method'].search(
            [('split_transactions', '=', False), ('is_cash_count', '=', True), ('company_id', '=', cls.env.company.id)],
            limit=1)

    def test_refund_origin(self):
        """ Test that original order is linked to the refund order """
        self.pos_config.open_session_cb()
        pos_session = self.pos_config.current_session_id
        pos_order = self.env['pos.order'].create({
            'company_id': self.env.company.id,
            'session_id': pos_session.id,
            'pricelist_id': self.partner_demo.property_product_pricelist.id,
            'partner_id': self.partner_demo.id,
            'lines': [(0, 0, {
                'product_id': self.env.ref('product.product_product_1').id,
                'qty': 1,
                'price_unit': 500,
                'discount': 0,
                'tax_ids': [[6, False, []]],
                'price_subtotal': 500,
                'price_subtotal_incl': 500,
            })],
            'amount_total': 500,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })

        payment_context = {"active_ids": pos_order.ids, "active_id": pos_order.id}
        order_payment = self.env['pos.make.payment'].with_context(**payment_context).create({
            'amount': pos_order.amount_total,
            'payment_method_id': self.cash_payment_method.id
        })
        order_payment.with_context(**payment_context).check()

        refund_act = pos_order.refund()
        refund = self.env['pos.order'].browse(refund_act['res_id'])
        # Expected result: original order appears in refund order
        self.assertEqual(refund.refund_original_order_id, pos_order)
