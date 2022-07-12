from datetime import timedelta
from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class VehicleTripStartWizard(models.TransientModel):
    _name = 'vehicle.trip.start.wizard'
    _inherit = 'abstract.vehicle.trip.wizard'
    _description = "Vehicle Trip Start Wizard"

    @api.model
    def _get_default_driver_id(self):
        return self.trip_id and self.trip_id.vehicle_id or False

    @api.model
    def _get_default_assistant_ids(self):
        return self.trip_id and self.trip_id.assistant_ids or False

    @api.model
    def _get_default_vehicle_id(self):
        return self.trip_id and self.trip_id.vehicle_id or False

    trip_id = fields.Many2one('fleet.vehicle.trip', domain=[('state', '=', 'confirmed')], ondelete='cascade')
    operation_start = fields.Datetime(string='Start Date', default=fields.Datetime.now, required=True)
    expected_end_date = fields.Datetime(string="Scheduled End Date", compute='_compute_expected_end_date',
                                        store=True,
                                        help='The expected end date of the trip which is automatically computed based on the total estimated time going through the selected route and on either the Operation Start date (actual start date)\n'
                                        ' or the Scheduled Start Date in case the trip is not started yet.')
    driver_id = fields.Many2one('res.partner', string='Driver', default=_get_default_driver_id, required=True, ondelete='cascade')
    assistant_ids = fields.Many2many('res.partner', string="Assistants", default=_get_default_assistant_ids,
                                     domain=[('is_company', '=', False)])
    vehicle_id = fields.Many2one('fleet.vehicle', default=_get_default_vehicle_id, required=True, string='Vehicle', ondelete='cascade')

    @api.depends('trip_id', 'trip_id.est_trip_time', 'operation_start')
    def _compute_expected_end_date(self):
        for r in self:
            if r.trip_id:
                r.expected_end_date = r.operation_start + timedelta(hours=r.trip_id.est_trip_time)
            else:
                r.expected_end_date = False

    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        if self.trip_id:
            self.driver_id = self.trip_id.driver_id
            self.assistant_ids = self.trip_id.assistant_ids
            self.vehicle_id = self.trip_id.vehicle_id

    @api.model
    def _prepare_start_data(self):
        res = {
            'state': 'progress',
            'operation_start': self.operation_start
               }

        # avoid write if field value no change
        if self.driver_id.id != self.trip_id.driver_id.id:
            res['driver_id'] = self.driver_id.id

        if self.vehicle_id.id != self.trip_id.vehicle_id.id:
            res['vehicle_id'] = self.vehicle_id.id

        if self.assistant_ids.ids != self.trip_id.assistant_ids.ids:
            res['assistant_ids'] = [(6, 0, self.assistant_ids.ids)]

        return res

    def action_start(self):
        Odometer = self.env['fleet.vehicle.odometer']
        for r in self:
            r.trip_id.write(self._prepare_start_data())
            r.trip_id.subscribe_drivers()

            odometer_zero_compare = float_compare(r.odometer, 0.0, precision_digits=2)
            if odometer_zero_compare == -1:
                raise ValidationError(_("The odometer number cannot be negative"))
            elif odometer_zero_compare == 0 and r.vehicle_id.odometer_count > 0:
                continue
            Odometer.create({
                'value': r.odometer,
                'date': r.operation_start or fields.Date.context_today(r),
                'vehicle_id': r.vehicle_id.id,
                'trip_id': r.trip_id.id
            })
