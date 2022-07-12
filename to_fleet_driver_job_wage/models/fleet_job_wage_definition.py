from odoo import models, fields, api


class FleetJobWageDefinition(models.Model):
    _name = 'fleet.job.wage.definition'
    _description = "Fleet Job Wage Definition"
    _inherit = 'mail.thread'

    @api.model
    def _get_default_service_type(self):
        return self.env.ref('to_fleet_driver_job_wage.fleet_driver_job_wage')

    route_id = fields.Many2one('route.route', string='Route', required=True, tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, tracking=True)
    consumption = fields.Float(string='Fuel Consumption (l)', required=True, tracking=True,
                              help="Estimated fuel consumption (in liters) for the selected vehicle on the selected route")
    allowance = fields.Float(string='Allowance', default=0.0, tracking=True,
                             help="Allowance for the driver of the trip on this route with this vehicle")
    fleet_service_type_id = fields.Many2one('fleet.service.type', string="Fleet Service Type",
                                            default=_get_default_service_type, required=True, ondelete='restrict')

    def get_consumption(self, route_id, vehicle_id):
        result = self.search([('route_id', '=', route_id.id), ('vehicle_id', '=', vehicle_id.id)], limit=1)
        return result

    def name_get(self):
        name = []
        for r in self:
            name.append((r.id, '%s / %s' % (r.vehicle_id.name, r.route_id.name)))
        return name

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('vehicle_id', 'ilike', name), ('route_id', 'ilike', name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
