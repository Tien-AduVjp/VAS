from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestSequenceEdit(TransactionCase):

    def setUp(self):
        super(TestSequenceEdit, self).setUp()
        # create partner
        self.partner_id = self.env['res.partner'].create({'name':'partner1'})
        # create product
        self.product_id = self.env['product.product'].create({'name':'product1'})
        # create uom_unit
        self.uom_unit = self.env.ref('uom.product_uom_unit')

    # create prepare_data
    def create_order_sequence(self, sequence_edit=False):
        order_id = self.env['purchase.order'].create({'partner_id':self.partner_id.id})
        order_line_data = {
            'product_id':self.product_id.id,
            'order_id':order_id.id,
            'product_uom':self.uom_unit.id,
            'name':'join',
            'date_planned':order_id.date_order,
            'product_qty':300,
            'price_unit':200,
            }
        if sequence_edit:
            order_line_data['sequence_edit'] = sequence_edit
        return self.env['purchase.order.line'].create(order_line_data)

    # test purchase line numbering
    def test_create_sequence(self):
        purchase_order = self.create_order_sequence()
        self.assertEqual(purchase_order.sequence, purchase_order.sequence_edit, "sequence is not equal sequence edit")
        purchase_order.write({'sequence':15})
        self.assertEqual(purchase_order.sequence_edit, 15, "sequence is not equal sequence edit")
        purchase_order.write({'sequence_edit':20})
        self.assertEqual(purchase_order.sequence, 20, "sequence is not equal sequence edit")

        purchase_order_2 = self.create_order_sequence(sequence_edit=50)
        self.assertEqual(purchase_order_2.sequence, purchase_order_2.sequence_edit, "sequence is not equal sequence edit")
