from odoo import fields, models, api

class AbstractVehicleTripWizard(models.AbstractModel):
    _name = 'abstract.vehicle.trip.wizard'
    _description = "Abstract model to share business logics between vehicle trip wizards"

    def _get_default_trip(self):
        return self.env['fleet.vehicle.trip'].browse(self._context.get('active_id'))

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', default=_get_default_trip, required=True, ondelete='cascade')
    odometer = fields.Float(string='Odometer Value', help='Odometer measure of the vehicle at the moment of this log')

    @api.onchange('trip_id')
    def onchange_trip_id(self):
        self.odometer = self.trip_id.vehicle_id.odometer
