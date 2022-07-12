from odoo.tests import SavepointCase, Form


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()

        cls.type_service = cls.env.ref('fleet.type_service_service_5')
        cls.product = cls.env.ref('product.product_product_4')
        cls.vehicle = cls.env.ref('fleet.vehicle_1')

    @classmethod
    def create_fleet_consumption_picking(cls, type_service, product, qty, vehicle, raw=False):
        picking_form = Form(cls.env['stock.picking'])
        picking_form.picking_type_id = cls.env.ref('to_fleet_stock.picking_type_fleet_consumption')
        picking_form.fleet_service_type_id = type_service
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = product
            move.product_uom_qty = qty
            move.vehicle_id = vehicle
        picking = picking_form.save()
        if not raw:
            picking.action_confirm()
            picking.action_assign()
            picking.move_ids_without_package[-1:].quantity_done = qty
            picking.button_validate()
        return picking
