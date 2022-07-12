from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    vehicle_revenue_id = fields.Many2one('fleet.vehicle.revenue', related='move_id.vehicle_revenue_id',
                                      ondelete='restrict', store=True, index=True,
                                      help="This field is to indicate that the analytic line relates to a vehicle revenue"
                                      " registered in the Fleet Management application")

    @api.constrains('vehicle_cost_id', 'vehicle_revenue_id')
    def _check_constrains_vehicle_revenue_revenue(self):
        for r in self:
            if r.vehicle_cost_id and r.vehicle_revenue_id:
                raise ValidationError(_("An analytic line cannot refer to both vehicle revenue and vehicle revenue. It is able to refer to either or neither of those"))

    @api.constrains('vehicle_revenue_id', 'vehicle_id')
    def _check_constrains_vehicle_revenue_id_vehicle_id(self):
        for r in self.filtered(lambda r: r.vehicle_revenue_id and r.vehicle_id):
            if r.vehicle_revenue_id.vehicle_id.id != r.vehicle_id.id:
                raise ValidationError(_("There is discrepancy between the Vehicle Revenue and the Vehicle."
                                        " The Vehicle Revenue is registered for the vehicle %s while the Vehicle"
                                        " on the move line is %s")
                                      % (r.vehicle_revenue_id.vehicle_id.display_name, r.vehicle_id.display_name))
