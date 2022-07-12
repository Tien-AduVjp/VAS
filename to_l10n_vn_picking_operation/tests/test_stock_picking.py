from datetime import date
from odoo.tests import TransactionCase
from odoo import fields

class TestStockPicking(TransactionCase):

    def setUp(self):
        super(TestStockPicking, self).setUp()

        self.stock_picking = self.env.ref('stock.incomming_shipment4')

    def test_compute_footer_date(self):
        new_date = date(2021, 9, 26)
        self.stock_picking.write({'date_done': new_date})
        self.assertEqual(self.stock_picking.footer_date, "Day 26 Month 9 Year 2021")

    def test_compute_total_amount_untaxed(self):
        self.stock_picking.move_lines.price_unit = 100
        self.assertEqual(self.stock_picking.total_amount_untaxed, 5000)

        self.stock_picking.move_lines.product_uom_qty = 10
        self.assertEqual(self.stock_picking.total_amount_untaxed, 1000)

        self.stock_picking.action_confirm()
        self.stock_picking.move_lines.quantity_done = 10
        self.stock_picking.move_lines.price_unit = 200
        self.stock_picking.state = 'done'
        self.stock_picking.flush()
        self.assertEqual(self.stock_picking.total_amount_untaxed, 2000)

    def test_unit_price_from_sale_order(self):
        """
            Input:
                The current currency of company by default (demo data) is USD
                Confirm a sale order with VND as the currency on trade:
                    price_unit:    1 billion VND
                    quantity:      2
            Expect:
                - With the rates setup, expect 1.000.000.000 VND = 58066,82 USD (approx.)
                - The price_unit on the generated stock move is converted from VND back to USD:
        """
        pricelist_vnd = self.env['product.pricelist'].create({
            'name': 'Test VND pricelist',
            'active': True,
            'currency_id': self.env.ref('base.VND').id,
            'company_id': self.env.company.id,
        })
        
        self.env.ref('base.rateUSDbis').write({
            'name': fields.Date.to_date('%s-01-01'%fields.Date.today().year),
            'rate': 1.528900
        })
        self.env.ref('base.VND').write({'rate': 26330.009999999998})
        
        partner = self.env.ref('base.res_partner_3')
        product = self.env.ref('product.product_product_7')
        
        so = self.env['sale.order'].create({
            'partner_id': partner.id,
            'date_order': fields.Datetime.now(),
            'pricelist_id': pricelist_vnd.id,
            'order_line': [
                (0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': 2,
                    'product_uom': product.uom_id.id,
                    'price_unit': 1000000000,   #    1.000.000.000
                    'tax_id': False,
                })
            ],
        })
        so.write({'state': 'sent'})
        so.action_confirm()

        total_amount_untaxed = so.picking_ids[0].total_amount_untaxed
        
        # With the rates above, expect 1.000.000.000 VND = 58066,82 USD (approx.)
        self.assertNotEqual(total_amount_untaxed, 1000000000)
        # 58066,82 * 2 = 116133.64 USD
        self.assertEqual(total_amount_untaxed, 116133.64)
