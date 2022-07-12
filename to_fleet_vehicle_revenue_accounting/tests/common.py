from odoo.tests.common import SavepointCase, Form
from addons import fleet


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.vehicle1 = cls.env.ref('fleet.vehicle_1')
        cls.vehicle2 = cls.env.ref('fleet.vehicle_2')

        cls.fleet_vehicle_revenue1 = cls.env['fleet.vehicle.revenue'].create({
            'vehicle_id': cls.vehicle1.id,
            'customer_id': cls.env.ref('base.res_partner_1').id
        })
        cls.invoice1 = cls.env['account.move'].create({
            'type': 'out_invoice',
            'partner_id': cls.env.ref('base.res_partner_2').id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': cls.env.ref('product.product_order_01').id,
                    'name': 'Car wash',
                    'quantity': 1,
                    'price_unit': 10
                })
            ]
        })
        cls.service_type1 = cls.env['fleet.service.type'].create({
            'name': 'Car wash',
            'product_id': cls.env.ref('product.product_order_01').id,
            'category': 'service'
        })
        cls.user_demo = cls.env.ref('base.user_demo')

    def create_fleet_vehicle_revenue_from_invoice_line(self, invoice_line, fleet_vehicle):
        wizard = self.env['vehicle.revenue.allocation.wizard'].create({
            'invoice_line_ids': invoice_line,
            'vehicle_ids': fleet_vehicle,
        })
        self.env['vehicle.revenue.allocation.line'].create({
            'vehicle_revenue_allocation_wizard_id': wizard.id,
            'invoice_line_id': invoice_line[0].id,
            'vehicle_id': fleet_vehicle.id,
            'amount': invoice_line[0].price_unit
        })
        wizard.create_vehicle_revenue()

    def create_invoice_from_vehicle_revenue(self, vehicle_revenue_ids):
        self.env['fleet.vehicle.revenue.invoicing.wizard'] \
            .with_context(active_ids=vehicle_revenue_ids.ids).create_invoices()
