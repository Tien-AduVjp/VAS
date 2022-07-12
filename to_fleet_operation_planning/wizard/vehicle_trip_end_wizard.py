from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class VehicleTripEndWizard(models.TransientModel):
    _name = 'vehicle.trip.end.wizard'
    _description = "Vehicle Trip End Wizard"
    _inherit = 'abstract.vehicle.trip.wizard'

    trip_id = fields.Many2one('fleet.vehicle.trip', domain=[('state', '=', 'progress')], ondelete='cascade')
    operation_end = fields.Datetime(string='End Date', default=fields.Datetime.now, required=True)
    fuel_consumption = fields.Float(string='Fuel Consumption', help="Fuel consumption (in liters) during the whole trip."
                                    " This information is just another figure beside fleet vehicle fuel logs")

    def action_done(self):
        Odometer = self.env['fleet.vehicle.odometer']
        for r in self:
            r.trip_id.write({
                'state': 'done',
                'operation_end': r.operation_end,
                'fuel_consumption': r.fuel_consumption
                })
            odometer_zero_compare = float_compare(r.odometer, 0.0, precision_digits=2)
            if odometer_zero_compare == -1:
                raise ValidationError(_("The odometer number cannot be negative"))
            elif odometer_zero_compare == 0:
                continue
            last_odometer = r.trip_id.odometer_ids[-1:]
            if last_odometer and r.odometer < last_odometer.value:
                raise ValidationError(_("The number of odometer at the end of a trip must not be less than the number of odometer when starting"))
            Odometer.create({
                'value': r.odometer,
                'date': r.operation_end or fields.Date.context_today(r),
                'vehicle_id': r.trip_id.vehicle_id.id,
                'trip_id': r.trip_id.id
            })
