# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    trip_id = fields.Many2one(related='picking_id.trip_id', store=True, readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', help="This is to indicate that this move concerns a vehicle")
    driver_id = fields.Many2one(related='picking_id.driver_id', store=True, readonly=True)

    @api.constrains('trip_id')
    def _check_vehicle_id(self):
        for r in self.filtered(lambda r: r.trip_id and r.vehicle_id):
            if r.trip_id.vehicle_id != r.vehicle_id:
                raise ValidationError(_("The vehicle of stock move '%s' must be the same as the vehicle of picking '%s'")
                                        % (r.name, r.picking_id.name)
                                        )

    def _update_vehicle_id(self, trip_id):
        trip = self.env['fleet.vehicle.trip'].browse(trip_id)
        self.write({
            'vehicle_id': trip and trip.vehicle_id.id or False,
            })
