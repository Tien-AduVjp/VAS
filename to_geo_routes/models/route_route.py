from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class RouteRoute(models.Model):
    _name = 'route.route'
    _description = 'Route'
    _inherit = ['mail.thread']

    name = fields.Char(string="Route name", required=True, translate=True, tracking=True)
    code = fields.Char(string='Code', help="The automatic generated unique code", default='/', required=True, readonly=True, copy=False)
    departure_id = fields.Many2one('res.partner', string="Departure", compute='_compute_dept_dest', store=True, tracking=True)
    destination_id = fields.Many2one('res.partner', string="Destination", compute='_compute_dept_dest', store=True, tracking=True)
    waypoint_ids = fields.One2many('route.waypoint', 'route_id', string="Waypoints", readonly=False, states={'confirmed': [('readonly', True)],
                                                                                                             'cancelled': [('readonly', True)]},
                                   help='List of points in the route where each point is linked to an address (model res.partner)')
    address_ids = fields.Many2many('res.partner',
                                   string="Addresses", compute='_compute_address_ids', store=True, index=True,
                                   help='The addresses that the route crosses')

    route_section_line_ids = fields.One2many('route.section.line', 'route_id', string='Sections', readonly=False,
                                             states={'confirmed': [('readonly', True)],
                                                     'cancelled': [('readonly', True)]}, compute='_compute_route_section_lines', store=True)

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
                             string='Status', required=True, default='draft', tracking=True)

    waypoint_ids_count = fields.Integer(string='Waypoints Count', compute='_compute_waypoints_count')
    total_distance = fields.Float(string='Total Distance (km)',
                                compute='_compute_total_distance', store=True, tracking=True,
                                help='Total Distance (in kilometers) of the route, which is automatically computed from the route section lines.')
    total_distance_in_miles = fields.Float(string='Total Distance (mi.)',
                                compute='_compute_total_distance_in_miles', store=True,
                                help='Total Distance (in miles) of the route, which is automatically computed from the route section lines.')
    average_speed = fields.Float(string='Average Speed', tracking=True,
                                 compute='_compute_average_speed', store=True,
                                 help='The average speed (in kilometer/hour) of the route, which is computed based on the max. speed on every section of the route.')
    est_trip_time = fields.Float(string='Est. Time', tracking=True,
                                 compute='_compute_est_trip_time', store=True,
                                 help='The estimated time in hours spent to go through the route (without any stop consideration)')

    def mile2km(self, miles):
        return self.env['route.section'].mile2km(miles)

    def km2mile(self, km):
        return self.env['route.section'].km2mile(km)

    @api.depends('route_section_line_ids.distance')
    def _compute_total_distance(self):
        for r in self:
            r.total_distance = sum(r.route_section_line_ids.mapped('distance'))

    @api.depends('route_section_line_ids.est_trip_time')
    def _compute_est_trip_time(self):
        for r in self:
            r.est_trip_time = sum(r.route_section_line_ids.mapped('est_trip_time'))

    @api.depends('total_distance', 'est_trip_time')
    def _compute_average_speed(self):
        for r in self:
            r.average_speed = r.total_distance / r.est_trip_time if r.est_trip_time > 0.0 else 0.0

    @api.depends('total_distance')
    def _compute_total_distance_in_miles(self):
        km2mile = self.env['to.base'].km2mile
        for r in self:
            r.total_distance_in_miles = km2mile(r.total_distance)

    @api.depends('waypoint_ids.sequence', 'waypoint_ids.address_id')
    def _compute_dept_dest(self):
        for r in self:
            waypoints = r.waypoint_ids.sorted('sequence')
            r.departure_id = waypoints[:1].address_id
            r.destination_id = waypoints[-1:].address_id

    @api.depends('waypoint_ids', 'waypoint_ids.address_id', 'waypoint_ids.sequence')
    def _compute_address_ids(self):
        for r in self:
            r.address_ids = r.waypoint_ids.mapped('address_id').ids

    @api.model
    def _prepare_route_section_line_data(self, address_from, address_to, sequence):
        section_id = self.env['route.section'].search([('address_from_id', '=', address_from.id), ('address_to_id', '=', address_to.id)], limit=1)
        return {
            'address_from_id': address_from.id,
            'address_to_id': address_to.id,
            'section_id': section_id and section_id.id or False,
            'sequence': sequence
            }

    @api.depends('waypoint_ids', 'waypoint_ids.sequence')
    def _compute_route_section_lines(self):
        for r in self:
            route_section_line_ids = [(3, section_line.id) for section_line in r.route_section_line_ids]
            last = False
            for waypoint in r.waypoint_ids.sorted(key='sequence'):
                if last:
                    route_section_line_ids.append((0, 0, r._prepare_route_section_line_data(last.address_id, waypoint.address_id, last.sequence)))
                last = waypoint

            for line in self.route_section_line_ids:
                route_section_line_ids.append((2, line.id))
            r.route_section_line_ids = route_section_line_ids

    @api.depends('waypoint_ids')
    def _compute_waypoints_count(self):
        total_wp_data = self.env['route.waypoint'].read_group([('route_id', 'in', self.ids)], ['route_id'], ['route_id'])
        mapped_data = dict([(dict_data['route_id'][0], dict_data['route_id_count']) for dict_data in total_wp_data])
        for r in self:
            r.waypoint_ids_count = mapped_data.get(r.id, 0)

    @api.constrains('waypoint_ids')
    def _check_waypoint_ids(self):
        for r in self:
            last_waypoint = False
            for waypoint in r.waypoint_ids.sorted('sequence'):
                if not last_waypoint:
                    last_waypoint = waypoint
                    continue
                if waypoint.address_id.id == last_waypoint.address_id.id:
                    raise ValidationError(_('The waypoint %s seems to be as the same as the preceding one. You cannot have'
                                            ' same waypoints those are adjacent to each other. I.e. A->B->B->C must be either A->B->C or A->B->C->B.')
                                          % waypoint.address_id.name)
                last_waypoint = waypoint

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        if any(r.state != 'cancelled' for r in self):
            raise UserError(_('You can only set-to-draft the routes those are in Cancelled state!'))
        self.write({'state': 'draft'})

    def get_addresses(self):
        return self.mapped('waypoint_ids.address_id')

    @api.model
    def find_by_addresses(self, addresses, exclude_self=True):
        """
        passing list of integer IDs then return routes that match
        """
        domain = []
        if self and exclude_self:
            domain += [('id', '!=', self.id)]
        domain += [('address_ids', 'in', addresses.ids)]

        # finding similar routes whose address_ids in the given address_ids
        similar_routes = self.search(domain)

        existing_routes = similar_routes.filtered(lambda route: route.get_addresses().ids == addresses.ids)
        return existing_routes or False

    @api.constrains('address_ids')
    def _check_constrains_address_ids(self):
        for r in self:
            existing_route = r.find_by_addresses(r.get_addresses())
            if existing_route:
                addresses = existing_route[0].get_addresses()
                string = ""
                for address in addresses:
                    string += address.name
                    string += '\n'
                raise UserError(_("You are about to create or update a route that has the same passing addresses"
                                  " as the existing one '%s' which also passes the same addresses as below:\n %s")
                                % (existing_route[0].name, string))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', '/') == '/':
                vals['code'] = self.env['ir.sequence'].next_by_code('geo.route.sequence')
        return super(RouteRoute, self).create(vals_list)

    @api.model
    def _generate_code_for_the_existing(self):
        """
        Added in version 0.2 when this version come with new field 'code' which stores sequence value
        """
        to_update = self.search(['|', ('code', '=', False), ('code', '=', '/')])
        Sequence = self.env['ir.sequence']
        for route in to_update:
            code = Sequence.next_by_code('geo.route.sequence')
            route.code = code

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, '[%s] %s' % (r.code, r.name)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', 'ilike', name), ('name', operator, name)]
        routes = self.search(domain + args, limit=limit)
        return routes.name_get()
