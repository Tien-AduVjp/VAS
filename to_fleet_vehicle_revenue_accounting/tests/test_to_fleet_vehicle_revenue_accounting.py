from odoo.tests.common import tagged, Form
from odoo.exceptions import UserError, ValidationError
from .common import Common


@tagged('post_install', '-at_install')
class TestToFleetVehicleRevenueAccounting(Common):

    def test_01_create_invoices_from_fleet_vehicle_revenue(self):
        # case 1:
        """ Case 1: Test create invoice from vehicle revenue.
                    Expect: create success
            Case 2: Test create invoice from vehicle revenue that has already been invoiced
                    Expect: create failure
        """
        self.assertFalse(self.fleet_vehicle_revenue1.invoice_line_id)

        self.create_invoice_from_vehicle_revenue(self.fleet_vehicle_revenue1)
        invoice_line = self.fleet_vehicle_revenue1.invoice_line_id

        self.assertEqual(invoice_line.move_id.state, 'draft')
        self.assertIn(self.fleet_vehicle_revenue1.id, invoice_line.fleet_vehicle_revenue_ids.ids)

        # case 2:
        with self.assertRaises(UserError):
            self.create_invoice_from_vehicle_revenue(self.fleet_vehicle_revenue1)

    def test_02_create_invoices_from_fleet_vehicle_revenue(self):
        # case 3:
        """ Test create invoice from vehicle revenue without `customer_id` in vehicle revenue
            Expect: create failure
        """
        self.fleet_vehicle_revenue1.customer_id = False
        with self.assertRaises(ValidationError):
            self.create_invoice_from_vehicle_revenue(self.fleet_vehicle_revenue1)

    def test_03_create_invoices_from_fleet_vehicle_revenue(self):
        # case 8:
        """ Test create invoice from vehicle revenue, invoice line is deleted in vehicle revenue record
            Expect: create invoice the second time successfully
        """
        self.create_invoice_from_vehicle_revenue(self.fleet_vehicle_revenue1)
        self.fleet_vehicle_revenue1.invoice_line_id = False
        self.create_invoice_from_vehicle_revenue(self.fleet_vehicle_revenue1)

    def test_create_vehicle_revenue_from_invoice(self):
        """ Test feature:
                "Accountant record customer invoices and allocated the invoice amounts across the vehicles of the fleet"
            Case 4:
                Input: create vehicle revenue from invocie
                Expect: automatically create a `fleet.vehicle.revenue` record associated with the invoice.
            Case 7:
                Input: allocate the invoice amounts across the vehicles of the fleet twice time
                Expect: the old `fleet.vehicle.revenue` record associated with the invoice is deleted
        """
        # case 4:
        self.assertFalse(self.invoice1.fleet_vehicle_revenue_ids)
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle1)

        # check information Fleet Vehicle Revenues is the same as invoice line
        fleet_vehicle_revenue = self.invoice1.fleet_vehicle_revenue_ids[0]
        self.assertTrue(fleet_vehicle_revenue)
        self.assertRecordValues(self.invoice1.invoice_line_ids[0], [
            {
                'product_id': fleet_vehicle_revenue.product_id.id,
                'price_subtotal': fleet_vehicle_revenue.amount,
            }
        ])
        self.assertEqual(fleet_vehicle_revenue.vehicle_id, self.vehicle1)

        # case 7:
        old_invoice_line = self.invoice1.fleet_vehicle_revenue_ids
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle2)

        self.assertFalse(old_invoice_line.exists())
        self.assertEqual(self.invoice1.fleet_vehicle_revenue_ids.vehicle_id, self.vehicle2)

    def test_check_constrains_product(self):
        # case 9:
        with self.assertRaises(ValidationError):
            self.env['fleet.vehicle.revenue'].create({
                'vehicle_id': self.vehicle1.id,
                'revenue_subtype_id': self.service_type1.id,
                'product_id': self.env.ref('product.product_product_3').id
            })

    def test_onchange_revenue_subtype_id(self):
        # case 10:
        with Form(self.env['fleet.vehicle.revenue']) as f:
            f.vehicle_id = self.vehicle1
            f.revenue_subtype_id = self.service_type1
            self.assertEqual(f.product_id, self.service_type1.product_id)

    def test_action_vehicle_revenue_allocation_wizard(self):
        # case 11:
        with self.assertRaises(UserError):
            self.env['account.move.line'].action_vehicle_revenue_allocation_wizard()

    def test_unlink_vehicle_revenue(self):
        # case 13:
        """ Test delete vehicle revenue record
            Expect: `fleet_vehicle_revenue_ids` in invoice is also deleted
        """
        self.create_invoice_from_vehicle_revenue(self.fleet_vehicle_revenue1)
        move_id = self.fleet_vehicle_revenue1.invoice_line_id.move_id
        self.assertTrue(move_id.fleet_vehicle_revenue_ids)

        self.fleet_vehicle_revenue1.unlink()
        self.assertFalse(move_id.fleet_vehicle_revenue_ids.exists())

    def test_unlink_invoice(self):
        # case 14:
        """
            Test: delete invoice
            Expect: vehicle revenue associated with the invoice is also deleted
        """
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle1)
        vehicle_revenue = self.invoice1.fleet_vehicle_revenue_ids
        self.assertTrue(vehicle_revenue)

        self.invoice1.unlink()
        self.assertFalse(vehicle_revenue.exists())

    def test_01_check_invl_vehicle_revenue_constrains(self):
        # case 15: test method _check_invl_vehicle_revenue_constrains
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle1)
        with self.assertRaises(ValidationError):
            self.invoice1.invoice_line_ids[0].price_unit = 200

    def test_02_check_invl_vehicle_revenue_constrains(self):
        # test method: _check_invl_vehicle_revenue_constrains
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle1)

        self.invoice1.fleet_vehicle_revenue_ids[0].currency_id = self.env.ref('base.VND')
        with self.assertRaises(ValidationError):
            self.invoice1.currency_id = self.env.ref('base.USD')
            self.invoice1.invoice_line_ids.price_subtotal = 21

    def test_cron_garbage(self):
        # test method: _cron_garbage
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle1)
        vehicle_revenue = self.invoice1.fleet_vehicle_revenue_ids[0]
        vehicle_revenue.invoice_line_id = False
        vehicle_revenue.created_from_invoice_line_id = self.invoice1.invoice_line_ids[0]

        vehicle_revenue.cron_garbage()
        self.assertFalse(vehicle_revenue.exists())
