from odoo import models, api
from odoo.tools import float_is_zero


class VehicleTripEndWizard(models.TransientModel):
    _inherit = 'vehicle.trip.end.wizard'

    def _prepare_cost_vals(self, fleet_service_type_id, amount):
        return {
            'trip_id': self.trip_id.id,
            'route_id': self.trip_id.route_id.id,
            'date':self.trip_id.operation_end,
            'vehicle_id': self.trip_id.vehicle_id.id,
            'vendor_id': self.trip_id.driver_id.id,
            'cost_subtype_id': fleet_service_type_id,
            'amount': amount,
            }

    @api.model
    def _prepare_cost_data_on_done(self):
        lines = []
        fleet_service_type_id = False
        if self.trip_id.job_wage_def_id and self.trip_id.job_wage_def_id.fleet_service_type_id:
            fleet_service_type_id = self.trip_id.job_wage_def_id.fleet_service_type_id.id

        if not float_is_zero(self.trip_id.fuel_based_job_wage, precision_digits=2):
            lines.append(self._prepare_cost_vals(fleet_service_type_id, self.trip_id.fuel_based_job_wage))

        if not float_is_zero(self.trip_id.job_allowance, precision_digits=2):
            lines.append(self._prepare_cost_vals(fleet_service_type_id, self.trip_id.job_allowance))

        return lines

    def action_done(self):
        super(VehicleTripEndWizard, self).action_done()
        Cost = self.env['fleet.vehicle.cost']
        for r in self:
            for line in r._prepare_cost_data_on_done():
                Cost.create(line)
