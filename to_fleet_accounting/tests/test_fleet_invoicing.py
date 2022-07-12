from odoo import fields
from odoo.tests import Form, tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestFleetAccounting(Common):

    @classmethod
    def setUpClass(cls):
        super(TestFleetAccounting, cls).setUpClass()

        cls.cost_1 = cls.generate_service_vehicle(cls.vehicle_1, cls.service_1, cls.vendor_1)
        cls.cost_2 = cls.generate_service_vehicle(cls.vehicle_2, cls.service_2, cls.vendor_1)

    def test_invoice_created_from_cost(self):
        self.assertTrue(self.cost_1.invoiceable)
        self.assertTrue(self.cost_2.invoiceable)

        invoice = self.create_invoice_from_services(self.cost_1)

        self.assertEqual(invoice.invoice_line_ids.fleet_vehicle_service_ids, self.cost_1 | self.cost_2)
        self.assertEqual(invoice.fleet_vehicle_service_ids, self.cost_1 | self.cost_2)
        self.assertFalse(self.cost_1.invoiceable)
        self.assertFalse(self.cost_2.invoiceable)

    def test_invoice_created_from_services_log(self):
        log_service = self.env['fleet.vehicle.log.services'].create({
                'vehicle_id': self.vehicle_1.id,
                'service_type_id': self.service_1.id,
                'vendor_id': self.vendor_2.id
            })
        self.env['fleet.vehicle.log.services.invoicing.wizard'].with_context(active_id=log_service.id,
                                                                             active_ids=log_service.ids).create_invoices()
        self.assertEqual(log_service.invoice_id.invoice_line_ids.fleet_vehicle_service_ids, log_service)
        self.assertFalse(log_service.invoiceable)

    def test_generate_analytic_line_after_post_invoice(self):
        invoice = self.create_invoice_from_services(self.cost_1)
        invoice.write({
            'invoice_date': fields.Date.today()
            })
        invoice.action_post()
        self.assertRecordValues(
            self.cost_1.invoice_line_id.analytic_line_ids,
            [
                {
                    'name': self.cost_1.vehicle_id.name,
                    'amount': -999,
                    'partner_id': self.cost_1.vendor_id.id,
                    'vehicle_service_id': self.cost_1.id,
                    'move_id': self.cost_1.invoice_line_id.id,
                    'product_id': self.cost_1.product_id.id
                    }
                ]
            )

    def test_distribution_service_on_invoice_line(self):
        invoice_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.service_1.product_id
            line.quantity = 1
            line.price_unit = 1000
        invoice_line = invoice_form.save().invoice_line_ids

        all_services_current = self.env['fleet.vehicle.log.services'].search([])
        service_distribution_wz = Form(self.env['vehicle.log.services.distribution'].with_context(active_ids=[invoice_line.id],
                                                                               active_id=invoice_line.id,
                                                                               default_invoice_line_ids=[invoice_line.id],
                                                                               active_model='account.move.line'))
        service_distribution_wz.vehicle_ids.add(self.vehicle_1)
        service_distribution_wz.vehicle_ids.add(self.vehicle_2)
        service_distribution_wz.save().create_vehicle_service()
        services_just_generated = self.env['fleet.vehicle.log.services'].search([]) - all_services_current
        self.assertRecordValues(
            services_just_generated,
            [
                {
                    'vehicle_id': self.vehicle_1.id,
                    'amount': 500,
                    'date': invoice_line.move_id.invoice_date,
                    'product_id': invoice_line.product_id.id,
                    'invoice_line_id': invoice_line.id,
                    'vendor_id': invoice_line.partner_id.id,
                    'created_from_invoice_line_id': invoice_line.id,
                    },
                {
                    'vehicle_id': self.vehicle_2.id,
                    'amount': 500,
                    'date': invoice_line.move_id.invoice_date,
                    'product_id': invoice_line.product_id.id,
                    'invoice_line_id': invoice_line.id,
                    'vendor_id': invoice_line.partner_id.id,
                    'created_from_invoice_line_id': invoice_line.id,
                    }
                ]

            )
