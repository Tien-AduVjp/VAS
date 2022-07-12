from odoo.tests.common import SavepointCase


class FleetAccountingFleetOperationCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(FleetAccountingFleetOperationCommon, cls).setUpClass()
        vehicle = cls.env.ref('fleet.vehicle_1')
        driver = cls.env.ref('base.res_partner_4')
        cls.trip = cls.env['fleet.vehicle.trip'].create({
            'vehicle_id': vehicle.id,
            'driver_id': driver.id,
            'expected_start_date': '2020-01-01 12:00:00'
        })
        cls.invoice = cls.env['account.move'].create({
            'type': 'in_invoice',
            'date': '2019-01-01',
            'invoice_line_ids': [
                (0, None, {
                    'product_id': cls.env.ref('product.consu_delivery_01').id,
                    'quantity': 1,
                    'price_unit': 100.0,
                }),
            ],
        })
        vehicle_cost_allocation_wizard = cls.env['vehicle.cost.distribution'].create({
            'vehicle_ids': [(6, 0, [vehicle.id])],
            'invoice_line_ids': [(6, 0, cls.invoice.invoice_line_ids.ids)],
            'vehicle_cost_allocation_line_ids': [
                (0, None, {
                    'invoice_line_id': cls.invoice.invoice_line_ids[0].id,
                    'vehicle_id':vehicle.id,
                    'trip_id':cls.trip.id,
                    'amount':100,
                }),
            ]
        })
        vehicle_cost_allocation_wizard.create_vehicle_cost()
        cls.vehicle_cost_uninvoice = cls.env['fleet.vehicle.cost'].create({
            'vendor_id': cls.env.ref('base.res_partner_address_1').id,
            'vehicle_id': vehicle.id,
        })
