from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, Form, tagged


@tagged('post_install', '-at_install')
class TestToPurchaseLandedCost(TransactionCase):

    def setUp(self):
        super(TestToPurchaseLandedCost, self).setUp()
        self.partner_1 = self.env['res.partner'].create({
            'name': 'partner test 1'
        })
        self.partner_2 = self.env['res.partner'].create({
            'name': 'partner test 2'
        })
        self.product_supplierinfo_1 = self.env['product.supplierinfo'].create({
            'name': self.partner_1.id
        })
        self.product_supplierinfo_2 = self.env['product.supplierinfo'].create({
            'name': self.partner_2.id
        })

        self.product_transport_1 = self.env['product.template'].create({
            'name': 'transport (landed cost) 1',
            'type': 'service',
            'seller_ids': [(6, 0, [self.product_supplierinfo_1.id])]
        })
        self.product_transport_2 = self.env['product.template'].create({
            'name': 'transport (landed cost) 2',
            'type': 'service',
            'seller_ids': [(6, 0, [self.product_supplierinfo_2.id])]
        })
        self.product_supplierinfo_1.product_tmpl_id = self.product_transport_1
        self.product_supplierinfo_2.product_tmpl_id = self.product_transport_2

        self.product_landed_cost_1 = self.env['product.landed.cost'].create({
            'product_template_id': self.product_transport_1.id,
            'product_id': self.product_transport_1.product_variant_id.id
        })
        self.product_landed_cost_2 = self.env['product.landed.cost'].create({
            'product_template_id': self.product_transport_2.id,
            'product_id': self.product_transport_2.product_variant_id.id
        })
        self.product_1 = self.env['product.template'].create({
            'name': 'Produck has landed cost 1',
            'type': 'product',
            'product_landed_cost_ids': [(6, 0, self.product_landed_cost_1.ids)]
        })
        self.product_2 = self.env['product.template'].create({
            'name': 'Produck has landed cost 2',
            'type': 'product',
            'product_landed_cost_ids': [(6, 0, self.product_landed_cost_2.ids)]
        })

    def test_01_onchange_order_line(self):
        # case 1:
        po_form = Form(self.env['purchase.order'])
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        self.assertEqual(po_form.purchase_landed_cost_ids._records[0]['product_id'], self.product_landed_cost_1.product_id.id)

    def test_02_onchange_order_line(self):
        # case 2
        self.product_landed_cost_1.auto_purchase = False
        po_form2 = Form(self.env['purchase.order'])
        with po_form2.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        self.assertEqual(len(po_form2.purchase_landed_cost_ids._records), 0)

    def test_01_create_purchase_order(self):
        # case 3:
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_2
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id

        po = po_form.save()
        po.button_confirm()
        po.flush()
        self.assertEqual(po.landed_cost_po_count, 1)
        self.assertTrue(po.landed_cost_po_ids[0].id != po.id)

    def test_02_create_purchase_order(self):
        # case 4:
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_1
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id

        po = po_form.save()
        po.button_confirm()
        self.assertEqual(len(po.order_line), 2)

    def test_03_create_purchase_order(self):
        # case 5:
        self.product_transport_1.seller_ids = False
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_1
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id

        po = po_form.save()
        with self.assertRaises(ValidationError):
            po.button_confirm()

    def test_04_create_purchase_order(self):
        # case 6:
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_1
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        po = po_form.save()

        po.button_confirm()
        self.assertEqual(len(po.order_line), 2)

        po.button_cancel()
        self.assertEqual(len(po.order_line), 1)

    def test_05_create_purchase_order(self):
        # case 10:
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_1
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        with po_form.order_line.new() as line2:
            line2.product_id = self.product_1.product_variant_id.copy()

        po = po_form.save()
        po.button_confirm()
        self.assertEqual(len(po.order_line), 3)

    def test_06_create_purchase_order(self):
        # case 11
        self.product_2.product_landed_cost_ids.product_id.seller_ids.name = self.partner_1
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_2
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        with po_form.order_line.new() as line2:
            line2.product_id = self.product_2.product_variant_id

        po = po_form.save()
        po.button_confirm()
        po.flush()
        self.assertEqual(len(po.landed_cost_po_ids.order_line), 2)

    def test_07_create_purchase_order(self):
        # case 12:
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_1
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        with po_form.order_line.new() as line2:
            line2.product_id = self.product_2.product_variant_id

        po = po_form.save()
        po.button_confirm()
        po.flush()

        self.assertEqual(len(po.order_line), 3)
        self.assertEqual(len(po.landed_cost_po_ids), 1)

    def test_08_create_purchase_order(self):
        # case 16:
        po_form_1 = Form(self.env['purchase.order'])
        po_form_1.partner_id = self.partner_2
        with po_form_1.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        po_1 = po_form_1.save()
        po_1.button_confirm()

        po_form_2 = Form(self.env['purchase.order'])
        po_form_2.partner_id = self.partner_2
        with po_form_2.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        po_2 = po_form_2.save()
        po_2.button_confirm()

        # Copy PO
        po_3 = po_2.copy()
        # Expect:
        #    No copy value of fields: landed_costs_for_po_ids, landed_cost_po_ids, stock_landed_cost_ids
        #    Copy landed_cost_po_ids
        self.assertRecordValues(
            po_3,
            [
                {
                    'landed_costs_for_po_ids': [],
                    'landed_cost_po_ids': [],
                    'stock_landed_cost_ids': [],
                    'landed_cost_po_ids': po_2.landed_cost_po_ids.ids,
                    }
                ]
            )

        # Expect:
        #    No copy value of fields: purchase_landed_cost_ids, landed_cost_for_po_ids
        self.assertRecordValues(
            po_3.order_line,
            [
                {
                    'purchase_landed_cost_ids': [],
                    'landed_cost_for_po_ids': [],
                    }
                ]
            )

        self.assertEqual(len(po_1.landed_cost_po_ids[0].order_line), 2)
        po_2.button_cancel()
        self.assertEqual(len(po_1.landed_cost_po_ids[0].order_line), 1)

    def test_09_create_purchase_order(self):
        """
        Raise error when there is a landed cost product in the RFQ that does not have a scheduled order date
        """
        po_form = Form(self.env['purchase.order'])
        po_form.partner_id = self.partner_2
        with po_form.order_line.new() as line:
            line.product_id = self.product_1.product_variant_id
        with po_form.purchase_landed_cost_ids.edit(0) as line:
            line.date_order = False
        po = po_form.save()
        with self.assertRaises(ValidationError):
            po.button_confirm()
