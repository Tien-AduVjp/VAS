from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestLineNumbering(TransactionCase):
    
    def setUp(self):
        super(TestLineNumbering, self).setUp()
        
        partner = self.env['res.partner'].create({'name': 'Tony'})
        order = self.env['sale.order'].create({'partner_id': partner.id})
        product = self.env['product.product'].create({'name': 'Table'})
        self.sale_order_line = self.env['sale.order.line'].create({
            'product_id': product.id,
            'order_id': order.id,
            'sequence': 15,
            })
    
    def test_sequence_edit(self):
        self.assertEqual(self.sale_order_line.sequence, self.sale_order_line.sequence_edit, "Sequence_edit is incorrect")
        self.sale_order_line.sequence_edit = 20
        self.assertEqual(self.sale_order_line.sequence, self.sale_order_line.sequence_edit, "Sequence is incorrect")
