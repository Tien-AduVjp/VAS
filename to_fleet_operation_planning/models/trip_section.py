from odoo import fields, models, api


class FleetVehicleTripSection(models.Model):
    _name = 'fleet.vehicle.trip.section'
    _description = 'Vehicle Trip Section'
    _rec_name = 'route_section_id'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', required=True, index=True, default=10)
    address_from_id = fields.Many2one('res.partner', string="From", required=True, index=True)
    address_to_id = fields.Many2one('res.partner', string="To", required=True, index=True)
    route_section_id = fields.Many2one('route.section', string='Section', readonly=True, ondelete='restrict', index=True)
    distance = fields.Float(string='Distance', help="The distance in kilometers between the From and To",
                            compute='_compute_distance_ave_speed', inverse='_set_distance_ave_speed', store=True,
                            required=True, default=0.0)
    ave_speed = fields.Float(string='Ave. Speed', help="The average speed in kilometer/hour that you can reach on this section",
                             compute='_compute_distance_ave_speed', inverse='_set_distance_ave_speed', store=True,
                             required=True, default=0.0)
    est_trip_time = fields.Float(string='Est. Duration',
                                 required=True, default=0.0,
                                 compute='_compute_est_trip_time', store=True,
                                 help="The estimated time in hours spent to go through the section")
    log_services_ids = fields.One2many('fleet.vehicle.log.services', 'trip_section_id', string='Services Logs')

    @api.depends('route_section_id', 'route_section_id.distance', 'route_section_id.ave_speed', 'trip_id.state')
    def _compute_distance_ave_speed(self):
        for r in self:
            if r.route_section_id:
                if r.trip_id.state == 'draft':
                    r.distance = r.route_section_id.distance
                    r.ave_speed = r.route_section_id.ave_speed
                else:
                    r.distance = r.distance
                    r.ave_speed = r.ave_speed
            else:
                r.distance = 0.0
                r.ave_speed = 0.0

    def _set_distance_ave_speed(self):
        # this is just to disable readonly mode
        pass

    @api.depends('distance', 'ave_speed')
    def _compute_est_trip_time(self):
        for r in self:
            if r.ave_speed:
                r.est_trip_time = r.distance / r.ave_speed
            else:
                r.est_trip_time = 0.0

    def _attach_section(self):
        """
        This method will look for a route.section record that matches address_from_id and address_to_id to the fleet.vehicle.trip.section' record's corresponding ones.
        If one found, it will attach the route.section record to the fleet.vehicle.trip.section'. Otherwise, new route.section record will be created to attach.
        """
        Section = self.env['route.section']
        sections = self.env['route.section'].search([('address_from_id', 'in', self.address_from_id.ids), ('address_to_id', 'in', self.address_to_id.ids)])
        for r in self:
            section_id = sections.filtered(lambda s: s.address_from_id == r.address_from_id and s.address_to_id == r.address_to_id)[:1]
            # create new section if not found
            if not section_id:
                section_id = Section.create({
                    'address_from_id': r.address_from_id.id,
                    'address_to_id': r.address_to_id.id,
                    'distance': r.distance,
                    'ave_speed': r.ave_speed,
                })
            r.write({
                'route_section_id': section_id.id,
                })

    @api.model_create_multi
    def create(self, vals_list):
        records = super(FleetVehicleTripSection, self).create(vals_list)
        records.filtered(lambda s: not s.route_section_id)._attach_section()
        return records

    def name_get(self):
        result = []
        for r in self:
            if r.route_section_id and r.trip_id:
                result.append((r.id, '[%s] %s' % (r.trip_id.name, r.route_section_id.name)))
            else:
                result.append((r.id, r.route_section_id.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('route_section_id.name', 'ilike', name), '|',
                      ('trip_id.name', operator, name), '|',
                      ('address_from_id.name', operator, name), ('address_to_id.name', operator, name)]
        tags = self.search(domain + args, limit=limit)
        return tags.name_get()

