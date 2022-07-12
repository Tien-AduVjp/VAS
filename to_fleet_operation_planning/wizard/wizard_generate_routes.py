from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WizardGenerateRoutes(models.TransientModel):
    _name = 'wizard.generate.routes'
    _description = 'Route Generator Wizard'

    update_trip = fields.Boolean(string='Update Trips', help="If checked, the routes selected below will be updated with new route.")
    type = fields.Selection([('all_trips', 'All Trips'), ('selected', 'Selected Trips')], required=True, default='selected')
    raise_error_if_dupplication_routes_found = fields.Boolean(string="Raise Error if Routes Duplication found", default=True,
                                                              help="Check this if you want to be warned when routes duplication found."
                                                              " In such the case, Odoo just tries to warn you if it find duplication."
                                                              " Routes will be generated only if no such the duplication found.")
    trip_ids = fields.Many2many('fleet.vehicle.trip', string='Trips')

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'all_trips':
            self.trip_ids = False

    def action_generate_routes(self):
        self.ensure_one()
        Trip = self.env['fleet.vehicle.trip']

        if self.type == 'all_trips':
            trip_ids = Trip.search([('trip_waypoint_ids', '!=', False)])
        else:
            trip_ids = self.trip_ids

        if not trip_ids:
            raise UserError(_("You must select at least one trip to proceed..."))

        for trip_id in trip_ids:
            route_id = trip_id.create_route_if_not_exist(raise_error_if_dupplication_found=self.raise_error_if_dupplication_routes_found)
            if self.update_trip and route_id.id != trip_id.route_id.id:
                    trip_id.route_id = route_id
