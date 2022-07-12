from odoo.tests import Form, tagged
from odoo.exceptions import UserError, ValidationError

from .common import Common


@tagged('post_install', '-at_install')
class TestCommonFleetAccouting(Common):

    @classmethod
    def setUpClass(cls):
        super(TestCommonFleetAccouting, cls).setUpClass()

        cls.cost_1 = cls.generate_service_vehicle(cls.vehicle_1, cls.service_1, cls.vendor_1)
        cls.company_2 = cls.env['res.company'].create({'name': 'Company 2'})


    def test_change_name_service(self):
        service_type = Form(self.service_1)
        service_type.product_id = self.service_2.product_id
        self.assertEqual(service_type.name, self.service_2.product_id.name)

    def test_autofill_cost_invoices_partner_change(self):
        # Create extra cost
        self.generate_service_vehicle(self.vehicle_1, self.service_2, self.vendor_1)

        invoice_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        invoice_form.partner_id = self.vendor_1
        self.assertEqual(len(invoice_form.invoice_line_ids._records), 2)

    def test_compute_invoiceable_cost(self):
        self.assertTrue(self.cost_1.invoiceable)
        invoice = self.create_invoice_from_services(self.cost_1)
        self.assertFalse(self.cost_1.invoiceable)


        cost_invoice_line = invoice.invoice_line_ids
        all_costs_current = self.env['fleet.vehicle.log.services'].search([])
        cost_distribution_wz = Form(self.env['vehicle.log.services.distribution'].with_context(active_ids=[cost_invoice_line.id],
                                                                                       active_id=cost_invoice_line.id,
                                                                                       default_invoice_line_ids=[cost_invoice_line.id],
                                                                                       active_model='account.move.line'))
        cost_distribution_wz.vehicle_ids.add(self.vehicle_1)
        cost_distribution_wz.save().create_vehicle_service()

        cost_just_generated = self.env['fleet.vehicle.log.services'].search([]) - all_costs_current
        self.assertFalse(cost_just_generated.invoiceable)


        cost_no_vendor = self.generate_service_vehicle(self.vehicle_1, self.service_1, False)
        self.assertFalse(cost_no_vendor.invoiceable)

    def test_generate_product_service(self):
        service_type = self.env['fleet.service.type'].create({'category': 'service', 'name': 'New service'})
        self.assertRecordValues(
            service_type.product_id,
            [
                {
                    'name': 'New service',
                    'type': 'service'
                    }
                ]
            )
        service_type_2 = self.env['fleet.service.type'].create({'category': 'service', 'name': 'New service'})
        self.assertEqual(service_type_2.product_id, service_type.product_id)

    def test_contrain_create_invoice_from_cost(self):
        cost = self.generate_service_vehicle(self.vehicle_1, self.service_1, False)
        with self.assertRaises(UserError):
            self.create_invoice_from_services(cost)

    def test_constrain_same_currency(self):
        invoice = self.create_invoice_from_services(self.cost_1)
        with self.assertRaises(ValidationError):
            invoice_form = Form(invoice)
            invoice_form.currency_id = self.env.ref('base.VND')
            invoice_form.save()

    def test_contraint_value_costs_equal_amount_invoice_line(self):
        invoice = self.create_invoice_from_services(self.cost_1)
        with self.assertRaises(ValidationError):
            invoice.invoice_line_ids.price_unit = 100

    def test_constraint_product_same_product_type_service(self):
        with self.assertRaises(ValidationError):
            self.cost_1.product_id = self.env.ref('fleet.type_service_service_3').product_id

    def test_constraint_save_company_on_vehicle_and_cost(self):
        with self.assertRaises(ValidationError):
            self.cost_1.company_id = self.company_2

    def test_constraint_change_name_analytic_account_vehicle(self):
        with self.assertRaises(UserError):
            self.vehicle_1.analytic_account_id.name = 'new name'

        self.vehicle_1.name = 'new name'
        self.vehicle_1.flush()
        self.assertEqual(self.vehicle_1.analytic_account_id.name, 'new name')
