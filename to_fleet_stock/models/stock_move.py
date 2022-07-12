from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    fleet_service_type_id = fields.Many2one('fleet.service.type', related='picking_id.fleet_service_type_id', store=True,
                                            help="The service type of the fleet related to this stock move")

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', help="This is to indicate that this move concerns a vehicle")

    @api.model
    def _get_vehicle_cost_location_type(self):
        return ['production', 'inventory']

    def _calculate_service_amount(self):
        self.ensure_one()
        amount = 0
        if self._is_out():
            amount = abs(sum(svl.value for svl in self.sudo().mapped('stock_valuation_layer_ids')))
        elif self._is_in():
            amount = -1 * abs(sum(svl.value for svl in self.sudo().mapped('stock_valuation_layer_ids')))
        return amount

    def _prepare_vehicle_services_data(self):
        self.ensure_one()
        res = {
            'vehicle_id': self.vehicle_id.id,
            'date': self.date,
            'quantity': self.product_qty,
            'amount': self._calculate_service_amount(),
            'created_from_stock_move_id': self.id,
            }

        if self.fleet_service_type_id:
            res['service_type_id'] = self.fleet_service_type_id.id

        return res

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder)

        FleetVehicleLogServices = self.env['fleet.vehicle.log.services']
        if not self.env.user.has_group('fleet.fleet_group_user'):
            FleetVehicleLogServices = FleetVehicleLogServices.sudo()

        for r in self:
            if r.vehicle_id:
                if r.location_dest_id.usage in r._get_vehicle_cost_location_type() or \
                r.location_id.usage in r._get_vehicle_cost_location_type():
                    FleetVehicleLogServices.create(r._prepare_vehicle_services_data())

        return res

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        res = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        res.append('vehicle_id')
        return res

