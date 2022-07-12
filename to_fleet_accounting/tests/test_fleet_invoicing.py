from odoo.tests import Form, tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestFleetAccounting(Common):
    
    @classmethod
    def setUpClass(cls):
        super(TestFleetAccounting, cls).setUpClass()
        
        cls.cost_1 = cls.generate_cost_vehicle(cls.vehicle_1, cls.service_1, cls.vendor_1)
        cls.cost_2 = cls.generate_cost_vehicle(cls.vehicle_2, cls.service_2, cls.vendor_1)

    def test_invoice_created_from_cost(self):
        self.assertTrue(self.cost_1.invoiceable)
        self.assertTrue(self.cost_2.invoiceable)
        
        invoice = self.create_invoice_from_costs(self.cost_1)

        self.assertEqual(invoice.invoice_line_ids.fleet_vehicle_cost_ids, self.cost_1 | self.cost_2)
        self.assertEqual(invoice.fleet_vehicle_cost_ids, self.cost_1 | self.cost_2)
        self.assertFalse(self.cost_1.invoiceable)
        self.assertFalse(self.cost_2.invoiceable)

    def test_invoice_created_from_services_log(self):
        log_service = self.env['fleet.vehicle.log.services'].create({
                'vehicle_id': self.vehicle_1.id,
                'cost_subtype_id': self.service_1.id,
                'vendor_id': self.vendor_2.id,
                'cost_ids': [(0, 0, {
                    'vehicle_id': self.vehicle_1.id,
                    'cost_subtype_id': self.service_2.id,
                    'vendor_id': self.vendor_1.id,
                    })]
            })
        self.env['fleet.vehicle.log.services.invoicing.wizard'].with_context(active_id=log_service.id,
                                                                             active_ids=log_service.ids).create_invoices()
        self.assertEqual(log_service.invoice_id.invoice_line_ids.fleet_vehicle_cost_ids, log_service.cost_id | log_service.cost_ids)
        self.assertFalse(log_service.cost_id.invoiceable)
        self.assertFalse(log_service.cost_ids.invoiceable)                                                                     

    def test_generate_analytic_line_after_post_invoice(self):
        invoice = self.create_invoice_from_costs(self.cost_1)
        invoice.action_post()
        self.assertRecordValues(
            self.cost_1.invoice_line_id.analytic_line_ids,
            [
                {
                    'name': self.cost_1.name,
                    'amount': -999,
                    'partner_id': self.cost_1.vendor_id.id,
                    'vehicle_cost_id': self.cost_1.id,
                    'move_id': self.cost_1.invoice_line_id.id,
                    'product_id': self.cost_1.product_id.id
                    }
                ]
            )
    
    def test_distribution_cost_on_invoice_line(self):
        invoice_form = Form(self.env['account.move'].with_context(default_type='in_invoice'))
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.service_1.product_id
            line.quantity = 1
            line.price_unit = 1000
        invoice_line = invoice_form.save().invoice_line_ids

        all_costs_current = self.env['fleet.vehicle.cost'].search([])
        cost_distribution_wz = Form(self.env['vehicle.cost.distribution'].with_context(active_ids=[invoice_line.id],
                                                                               active_id=invoice_line.id,
                                                                               default_invoice_line_ids=[invoice_line.id],
                                                                               active_model='account.move.line'))
        cost_distribution_wz.vehicle_ids.add(self.vehicle_1)
        cost_distribution_wz.vehicle_ids.add(self.vehicle_2)
        cost_distribution_wz.save().create_vehicle_cost()
        costs_just_generated = self.env['fleet.vehicle.cost'].search([]) - all_costs_current
        self.assertRecordValues(
            costs_just_generated,
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
