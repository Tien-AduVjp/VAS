from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    trip_ids = fields.One2many('fleet.vehicle.trip', 'vehicle_id', string='Trips',
                               help="The Trips that refer to this vehicle")

    scheduled_trips_count = fields.Integer(string='Schedule Trips Count', compute='_compute_scheduled_trips_count')

    next_scheduled_trip_id = fields.Many2one('fleet.vehicle.trip', string='Next Scheduled Trip', compute='_compute_next_scheduled_trip', store=True)
    next_scheduled_trip_date = fields.Datetime(string='Next Trip Date', compute='_compute_next_scheduled_trip', store=True)

    access_partner_ids = fields.Many2many('res.partner', string='Access Partner', compute='_compute_access_partner_ids', store=True,
                                         help="The partners who has access to this vehicle which is computed how"
                                         " the partners are set as the driver for the trips of this vehicle."
                                         " For example. assume Mr. A is set as the driver for a trip of this vehicle."
                                         " He will have access to the vehicle information as long as the trip is either"
                                         " in Confirmed or in In-Operation state")

    operation_hours = fields.Float(string='Operation Hours', compute='_compute_total_operation_hours', store=True,
                                 help="The total operation hours of the vehicle which is computed by summary of the total hours"
                                 " of the done trips with the vehicle")

    operation_distance = fields.Float(string='Operation Distance', compute='_compute_total_operation_distance', store=True,
                                      help="The total operation distance of the vehicle which is computed by summary of the total actual distance"
                                      " of the done trips with the vehicle")
    address_id = fields.Many2one('res.partner', string='Default Address',
                                 help="The default address of the vechile (e.g. garage, station, etc)")

    @api.depends('trip_ids', 'trip_ids.state', 'trip_ids.operation_duration')
    def _compute_total_operation_hours(self):
        for r in self:
            r.operation_hours = sum(r.trip_ids.filtered(lambda t: t.state == 'done').mapped('operation_duration'))

    @api.depends('trip_ids', 'trip_ids.state', 'trip_ids.actual_distance')
    def _compute_total_operation_distance(self):
        for r in self:
            r.operation_distance = sum(r.trip_ids.filtered(lambda t: t.state == 'done').mapped('actual_distance'))

    @api.depends('trip_ids', 'trip_ids.start_date', 'trip_ids.state')
    def _compute_next_scheduled_trip(self):
        for r in self:
            trip_ids = r.trip_ids.filtered(lambda t: t.state == 'confirmed')
            if trip_ids:
                r.next_scheduled_trip_id = trip_ids[0]
                r.next_scheduled_trip_date = trip_ids[0].start_date
            else:
                r.next_scheduled_trip_id = False
                r.next_scheduled_trip_date = False

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.address_id = self.company_id.partner_id

    def migrate_location_to_address(self):
        ResPartner = self.env['res.partner']
        for r in self:
            address_id = False
            if r.location:
                address_id = ResPartner.search([('name', '=', r.location)], limit=1)
                if not address_id:
                    address_id = ResPartner.search([('name', 'ilike', r.location)], limit=1)
                if not address_id:
                    address_id = ResPartner.create({'name':r.location})
            else:
                if r.company_id:
                    address_id = r.company_id.partner_id
            if address_id:
                r.address_id = address_id

    @api.model
    def _get_default_address(self):
        address_id = False
        if self.location:
            ResPartner = self.env['res.partner']
            address_id = ResPartner.search([('name', '=', self.location)], limit=1)
            if not address_id:
                address_id = ResPartner.search([('name', 'ilike', self.location)], limit=1)
        if not address_id and self.company_id:
            address_id = self.company_id.partner_id
        return address_id

    def _compute_scheduled_trips_count(self):
        for r in self:
            r.scheduled_trips_count = len(r.trip_ids.filtered(lambda t: t.state == 'confirmed'))

    @api.depends('trip_ids', 'trip_ids.state', 'trip_ids.driver_id', 'trip_ids.vehicle_id')
    def _compute_access_partner_ids(self):
        trips = self.env['fleet.vehicle.trip'].sudo().search([('state', 'in', ('confirmed', 'progress')), ('driver_id', '!=', False), ('vehicle_id', 'in', self.ids)])
        for r in self:
            active_trips = trips.filtered(lambda t: t.vehicle_id.id == r.id)
            if active_trips:
                driver_ids = active_trips.mapped('driver_id')
                r.access_partner_ids = [(6, 0, driver_ids.ids)]
            else:
                r.access_partner_ids = False

    def action_view_scheduled_trips(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_fleet_operation_planning.fleet_confirmed_trip_action')

        action.pop('id', None)

        # reset domain to show no trip
        action['domain'] = [('id','<',0)]

        # reset context and add some default values
        action['context'] = {'default_vehicle_id':self.id}
        if self.driver_id:
            action['context']['driver_id'] = self.driver_id.id

        trip_ids = self.trip_ids.filtered(lambda t: t.state == 'confirmed')
        # choose the view_mode accordingly
        if len(trip_ids) > 1:
            action['domain'] = [('id','in', trip_ids.ids)]
        elif len(trip_ids) == 1:
            res = self.env.ref('to_fleet_operation_planning.fleet_trip_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = trip_ids[0].id

        return action
