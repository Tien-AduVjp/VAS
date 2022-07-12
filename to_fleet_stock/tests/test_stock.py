from odoo.exceptions import ValidationError
from odoo.addons.base.models.qweb import QWebException
from odoo.tests import Form, tagged

from .common import Common


@tagged('post_install', '--at_install')
class TestStock(Common):

    def test_generate_services_by_done_picking(self):
        picking = self.create_fleet_consumption_picking(self.type_service, self.product, 2, self.vehicle)
        service_generate = self.env['fleet.vehicle.log.services'].search([('created_from_stock_stock_picking_id', '=', picking.id)])
        self.assertEqual(len(service_generate), 1)
        self.assertEqual(service_generate.service_type_id, self.type_service)
        self.assertEqual(service_generate.amount, self.product.standard_price * 2)

    def test_merge_stock_move(self):
        # Condition to merge stock move when confirm picking
        picking = self.create_fleet_consumption_picking(self.type_service, self.product, 1, self.vehicle, raw=True)
        with Form(picking) as fleet_picking:
            with fleet_picking.move_ids_without_package.new() as move:
                move.product_id = self.product
                move.product_uom_qty = 1
                move.vehicle_id = self.env.ref('fleet.vehicle_2')

        with self.assertRaises(QWebException), self.cr.savepoint():
            picking.action_confirm()
            self.assertEqual(len(picking.move_ids_without_package), 2)
            raise QWebException("Trick to rollback")

        picking.move_ids_without_package[-1:].vehicle_id = self.env.ref('fleet.vehicle_1')
        picking.action_confirm()
        self.assertEqual(len(picking.move_ids_without_package), 1)
        self.assertEqual(picking.move_ids_without_package.product_uom_qty, 2)

    def test_constrain_vehicle_on_stock_move(self):
        # Check constrain require vehicle on stock move, fleet service type on picking when validate picking
        picking = self.create_fleet_consumption_picking(self.type_service, self.product, 1, self.vehicle)
        with self.assertRaises(ValidationError):
            picking.move_ids_without_package[-1:].vehicle_id = False
            picking.action_confirm()

        picking.fleet_service_type_id = False
        with self.assertRaises(ValidationError):
            picking.action_confirm()
