from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    vehicle_service_id = fields.Many2one('fleet.vehicle.log.services', string="Vehicle Service",
                                      ondelete='restrict', index=True,
                                      help="This field is to indicate that the analytic line relates to a vehicle service"
                                      " registered in the Fleet Management application")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', related='vehicle_service_id.vehicle_id',
                                 store=True, index=True, ondelete='restrict',
                                 help="The vehicle to which this move line refers")

    @api.constrains('vehicle_service_id', 'vehicle_id')
    def _check_constrains_vehicle_service_id_vehicle_id(self):
        for r in self:
            if r.vehicle_service_id and r.vehicle_id:
                if r.vehicle_service_id.vehicle_id.id != r.vehicle_id.id:
                    raise ValidationError(_("There is discrepancy between the Vehicle Sevice and the Vehicle."
                                            " The Vehicle Service is registered for the vehicle %s while the Vehicle"
                                            " on the move line is %s")
                                          % (r.vehicle_service_id.vehicle_id.display_name, r.vehicle_id.display_name))

