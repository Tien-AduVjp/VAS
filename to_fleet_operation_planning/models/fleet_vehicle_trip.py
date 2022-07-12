from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
from odoo.tools import float_is_zero

import logging

_logger = logging.getLogger(__name__)


class FleetVehicleTrip(models.Model):
    _name = 'fleet.vehicle.trip'
    _description = 'Fleet Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, end_date desc, name, id'

    name = fields.Char(string="Reference", required=True, readonly=True, copy=False, default='/')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", index=True, readonly=False, required=True, ondelete='restrict',
                                 states={'confirmed': [('readonly', True)],
                                         'progress': [('readonly', True)],
                                         'done': [('readonly', True)],
                                         'cancelled': [('readonly', True)]}, tracking=True,
                                 help="The vehicle, which can be changed upon starting the trip")
    driver_id = fields.Many2one('res.partner', string="Driver", readonly=False, ondelete='restrict', required=True,
                                states={'confirmed': [('readonly', True)],
                                         'progress': [('readonly', True)],
                                         'done': [('readonly', True)],
                                         'cancelled': [('readonly', True)]}, tracking=True,
                                help="The driver, that can be changed upon starting the trip")

    employee_id = fields.Many2one('hr.employee', string='Employee', compute='_compute_employee_id', store=True, index=True,
                                  help='The employee who acts as the driver for the trip')

    assistant_ids = fields.Many2many('res.partner', 'assistant_trip_rel', 'trip_id', 'assistant_id', string="Assistants", readonly=False,
                                     states={'confirmed': [('readonly', True)],
                                              'progress': [('readonly', True)],
                                              'done': [('readonly', True)],
                                              'cancelled': [('readonly', True)]},
                                     domain=[('is_company', '=', False)])
    route_id = fields.Many2one('route.route', string="Route", readonly=False, states={'confirmed': [('readonly', True)],
                                                                                      'progress': [('readonly', True)],
                                                                                      'done': [('readonly', True)],
                                                                                      'cancelled': [('readonly', True)]},
                               domain=[('state', '=', 'confirmed')],
                               help="The route through which the vehicle of this trip will go. Leave this empty and specify waypoints"
                               " in the section below will automatically select a matched route (if exists) or create a new route"
                               " containing the waypoints you specify",
                               ondelete='restrict', tracking=True)

    expected_start_date = fields.Datetime(string="Scheduled Start Date", required=True,
                                          readonly=False, states={'progress': [('readonly', True)],
                                                                  'done': [('readonly', True)],
                                                                  'cancelled': [('readonly', True)]},
                                          default=fields.Datetime.now(),
                                          tracking=True,
                                          help='The expected / planned start date of the trip')
    expected_end_date = fields.Datetime(string="Scheduled End Date", compute='_compute_expected_end_date',
                                        readonly=False, states={'progress': [('readonly', True)],
                                                                'done': [('readonly', True)],
                                                                'cancelled': [('readonly', True)]},
                                        store=True, tracking=True,
                                        help='The expected end date of the trip which is automatically computed based on the total estimated time going through the selected route and on either the Operation Start date (actual start date)\n'
                                        ' or the Scheduled Start Date in case the trip is not started yet.')

    operation_start = fields.Datetime(string="Operation Start Date", readonly=True, tracking=True,
                                      help='The actual start date of the trip which is automatically recorded when Start Trip button is pressed.')
    operation_end = fields.Datetime(string="Operation End Date", readonly=True, tracking=True,
                                    help='The actual end date of the trip which is automatically recorded when Done button is pressed.')
    operation_duration = fields.Float(string="Actual Duration", compute='_compute_operation_duration', store=True,
                                      help='The actual operation duration (in hours) which is computed from the Operation Start Date and the Operation End Date')

    start_date = fields.Datetime(string="Start Date", compute='_compute_start_date', store=True, index=True,
                                 help='This is the Scheduled Start Date when the operation is not been started. Otherwise, it will be Operation Start Date')
    end_date = fields.Datetime(string="End Date", compute='_compute_end_date', store=True, index=True,
                                 help='This is the Scheduled End Date when the operation is not been done. Otherwise, it will be Operation End Date')

    description = fields.Text(string="Description")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Operation'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="Status", index=True, readonly=True, tracking=True, copy=False, default='draft', required=True)

    trip_waypoint_ids = fields.One2many('fleet.vehicle.trip.waypoint', 'trip_id', string='Waypoints', index=True)

    trip_section_ids = fields.One2many('fleet.vehicle.trip.section', 'trip_id', string='Trip Sections', index=True)

    est_distance = fields.Float(string='Est. Distance', compute='_compute_est_distance', store=True)

    odometer_unit = fields.Selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], related='vehicle_id.odometer_unit', readonly=True, store=True)

    est_trip_time = fields.Float(string='Est. Duration', compute='_compute_est_trip_time', store=True,
                                 help='The estimated time in hours spent to go through the route (including stop duration)')

    time_deviation = fields.Float(string='Time Deviation', help='The time deviation (in hours) between actual operation duration planned duration'
                                  ' which is computed by Actual Duration minus Est. Duration.', compute='_compute_time_deviation', store=True, index=True)
    operator_id = fields.Many2one('res.users', string='Operator', default=lambda self: self.env.user,
                                  readonly=False, states={'confirmed': [('readonly', True)],
                                                          'progress': [('readonly', True)],
                                                          'done': [('readonly', True)],
                                                          'cancelled': [('readonly', True)]},
                                  help="The operation user who takes the responsibility for this trip")

    fleet_vehicle_cost_ids = fields.One2many('fleet.vehicle.cost', 'trip_id', string='Vehicle Costs')
    fleet_vehicle_costs_count = fields.Integer(string='Vehicle Costs Count', compute='_compute_fleet_vehicle_costs_count', store=True)

    odometer_ids = fields.One2many('fleet.vehicle.odometer', 'trip_id', string='Odometer')
    actual_distance = fields.Float(string='Actual Distance', compute='_compute_actual_distance', store=True,
                                   help='The actual Distance of the trip which is computed by the start odometer and end odometer')
    distance_unit = fields.Selection(related='vehicle_id.odometer_unit', string='Distance Unit', readonly=True, store=True)

    distance_deviation = fields.Float(string='Distance Deviation', help='The distance deviation between the actual operation distance and the planned distance',
                                      compute='_compute_distance_deviation', store=True, index=True)
    fuel_consumption = fields.Float(string='Fuel Consumption', tracking=True, help="Fuel consumption (in liters) during the whole trip."
                                    " This information is just another figure beside fleet vehicle fuel logs")
    average_fuel_consumption_per_hundred = fields.Float(string='Ave. Fuel Consumption per Hundred', compute='_compute_average_fuel_consumption_per_hundred')

    @api.depends('driver_id')
    def _compute_employee_id(self):
        employees = self.env['hr.employee'].sudo().search([('address_home_id', 'in', self.driver_id.ids)])
        for r in self:
            r.employee_id = employees.filtered(lambda e: e.address_home_id == r.driver_id)[:1]

    @api.depends('fuel_consumption', 'actual_distance')
    def _compute_average_fuel_consumption_per_hundred(self):
        for r in self:
            if not float_is_zero(r.actual_distance, precision_digits=2):
                r.average_fuel_consumption_per_hundred = r.fuel_consumption * 100 / r.actual_distance
            else:
                r.average_fuel_consumption_per_hundred = 0.0

    @api.depends('odometer_ids', 'odometer_ids.value')
    def _compute_actual_distance(self):
        for r in self:
            actual_distance = 0.0
            i = 0
            for odometer in r.odometer_ids.sorted(key='date', reverse=True):
                if i > 0:
                    actual_distance += odometer.value - r.odometer_ids[i - 1].value
                i += 1
            r.actual_distance = actual_distance

    @api.depends('actual_distance', 'est_distance')
    def _compute_distance_deviation(self):
        for r in self:
            r.distance_deviation = r.actual_distance - r.est_distance

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.driver_id = self.vehicle_id.driver_id

    @api.depends('fleet_vehicle_cost_ids')
    def _compute_fleet_vehicle_costs_count(self):
        costs = self.env['fleet.vehicle.cost'].read_group([('trip_id', 'in', self.ids)], ['trip_id'], ['trip_id'])
        mapped_data = dict([(c['trip_id'][0], c['trip_id_count']) for c in costs])
        for r in self:
            r.fleet_vehicle_costs_count = mapped_data.get(r.id, 0)

    def name_get(self):
        result = []
        for r in self:
            if r.route_id:
                result.append((r.id, "%s [%s] [%s]" % (r.name, r.sudo().vehicle_id.display_name, r.route_id.display_name,)))
            else:
                result.append((r.id, "%s [%s]" % (r.name, r.vehicle_id.display_name,)))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        name search that supports searching by rule and code and times
        """
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('route_id.name', 'ilike', name), ('vehicle_id.license_plate', 'ilike', name), ('name', operator, name)]
        rules = self.search(domain + args, limit=limit)
        return rules.name_get()

    @api.depends('est_trip_time', 'operation_duration')
    def _compute_time_deviation(self):
        for r in self:
            if r.est_trip_time > 0 and r.operation_duration > 0:
                r.time_deviation = r.operation_duration - r.est_trip_time
            else:
                r.time_deviation = 0.0

    def mile2km(self, miles):
        return self.env['route.route'].mile2km(miles)

    def km2mile(self, km):
        return self.env['route.route'].km2mile(km)

    @api.depends('trip_section_ids', 'trip_section_ids.distance', 'odometer_unit')
    def _compute_est_distance(self):
        for r in self:
            est_distance = sum(r.trip_section_ids.mapped('distance'))
            if r.odometer_unit == 'miles':
                est_distance = self.km2mile(est_distance)
            r.est_distance = est_distance

    @api.depends('expected_start_date', 'operation_start')
    def _compute_start_date(self):
        for r in self:
            if r.operation_start:
                r.start_date = r.operation_start
            elif r.expected_start_date:
                r.start_date = r.expected_start_date
            else:
                r.start_date = r.start_date or fields.Datetime.now()
    
    @api.depends('start_date', 'operation_end', 'expected_end_date', 'est_trip_time')
    def _compute_end_date(self):
        for r in self:
            if r.operation_end:
                r.end_date = r.operation_end
            elif r.expected_end_date:
                r.end_date = r.expected_end_date
            elif r.start_date:
                r.end_date = r.start_date + timedelta(hours=r.est_trip_time)
            else:
                r.end_date = r.end_date or False

    @api.depends('expected_start_date', 'est_trip_time')
    def _compute_expected_end_date(self):
        for r in self:
            if r.expected_start_date and r.est_trip_time:
                r.expected_end_date = r.expected_start_date + timedelta(hours=r.est_trip_time)
            else:
                r.expected_end_date = r.expected_end_date or False

    @api.depends('trip_waypoint_ids', 'trip_waypoint_ids.stop_duration', 'trip_section_ids', 'trip_section_ids.est_trip_time')
    def _compute_est_trip_time(self):
        for r in self:
            total_stop_duration = sum(r.trip_waypoint_ids.mapped('stop_duration'))
            total_section_duration =  sum(r.trip_section_ids.mapped('est_trip_time'))
            r.est_trip_time = total_stop_duration + total_section_duration

    @api.depends('operation_start', 'operation_end')
    def _compute_operation_duration(self):
        for r in self:
            if r.operation_start and r.operation_end:
                delta = r.operation_end - r.operation_start
                r.operation_duration = delta.total_seconds() / 3600
            else:
                r.operation_duration = 0.0

    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id:
            trip_waypoint_ids = self.route_id._prepare_trip_waypoints_data(self)
            for line in self.trip_waypoint_ids:
                trip_waypoint_ids.append((2, line.id))
            self.trip_waypoint_ids = trip_waypoint_ids

    @api.onchange('trip_waypoint_ids')
    def _onchange_trip_waypoint_ids(self):
        # sorting input waypoints by sequence
        # we cannot use self.waypoint_ids.sorted(key='sequence') since waypoints has not been saved into database yet.
        waypoints = self.trip_waypoint_ids.sorted(key='sequence', reverse=False)

        Section = self.env['route.section']

        trip_section_ids = []
        last_waypoint = False
        for waypoint in waypoints:
            if last_waypoint:
                section_id = Section.search([('address_from_id', '=', last_waypoint.address_id.id), ('address_to_id', '=', waypoint.address_id.id)], limit=1)

                data = {
                    'trip_id': self.id,
                    'address_from_id': last_waypoint.address_id.id,
                    'address_to_id': waypoint.address_id.id,
                    }
                if section_id:
                    data['route_section_id'] = section_id.id
                    data['distance'] = section_id.distance
                    data['ave_speed'] = section_id.ave_speed
                trip_section_ids.append((0, 0, data))

            last_waypoint = waypoint
        for line in self.trip_section_ids:
            trip_section_ids.append((2, line.id))

        self.trip_section_ids = trip_section_ids

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        res = {}
        if self.driver_id:
            res['domain'] = {'assistant_ids': [('id', '!=', self.driver_id.id), ('is_company', '=', False)]}
        return res

    @api.constrains('driver_id', 'assistant_ids')
    def _check_driver(self):
        for r in self:
            if r.driver_id and r.assistant_ids:
                if r.driver_id.id in r.assistant_ids.ids:
                    raise UserError(_('Driver and Assistant must not be the same person.'
                                      ' Please either change the driver or remove him from assistant tag box.'))

    @api.constrains('operation_end', 'operation_start')
    def _check_operation_dates(self):
        for r in self:
            if r.operation_start and r.operation_end:
                if r.operation_end < r.operation_start:
                    raise UserError(_("The Operation End Date must be greater than the Operation Start Date."))

    @api.constrains('start_date', 'end_date')
    def _check_start_date_end_date(self):
        for r in self:
            if r.est_trip_time > 0.0:
                if r.start_date and r.end_date:
                    if r.start_date >= r.end_date:
                        raise UserError(_('The Start Date must be prior to the End Date'))

    @api.constrains('vehicle_id', 'start_date', 'end_date', 'driver_id', 'state')
    def check_operation_overlap(self):
        for r in self:
            if r.state == 'confirmed':
                # overlap checking
                #  1. planned start date within an existing confirmed trip duration, OR
                #  2. planned end date within an existing confirmed trip duration
                overlap_domain = [('start_date', '<', r.end_date), ('end_date', '>', r.start_date),
                                  ('id', '!=', r.id), ('state', 'in', ('confirmed', 'progress'))]

                # check if same vehicle is planned for same time:
                domain = [('vehicle_id', '=', r.vehicle_id.id), ('vehicle_id', '!=', False)] + overlap_domain
                overlap = self.search(domain, limit=1)
                if overlap:
                    start_date = fields.Datetime.context_timestamp(r, overlap.start_date)
                    end_date = fields.Datetime.context_timestamp(r, overlap.end_date)
                    raise UserError(_('Overlapping! You cannot confirm this trip for vehicle "%s" since there is\n'
                                      ' another trip "%s" has been confirmed and scheduled for this vehicle at the time frame which is %s and %s.')
                                    % (r.vehicle_id.name, overlap.name, start_date, end_date))

                # check if same driver is planned for same time:
                domain = [('driver_id', '=', r.driver_id.id), ('driver_id', '!=', False)] + overlap_domain
                overlap = self.search(domain, limit=1)
                if overlap:
                    start_date = fields.Datetime.context_timestamp(r, overlap.start_date)
                    end_date = fields.Datetime.context_timestamp(r, overlap.end_date)
                    raise UserError(_('Overlapping! You cannot confirm this trip for driver "%s" since there is\n'
                                      ' another trip "%s" has been confirmed and scheduled for this driver at the time frame which is %s and %s.')
                                    % (r.driver_id.name, overlap.name, start_date, end_date))

    @api.constrains('trip_waypoint_ids')
    def _check_waypoint_ids(self):
        for r in self:
            last_waypoint = False
            for waypoint in r.trip_waypoint_ids.sorted('sequence'):
                if not last_waypoint:
                    last_waypoint = waypoint
                    continue
                if waypoint.address_id.id == last_waypoint.address_id.id:
                    raise ValidationError(_('The waypoint %s seems to be as the same as the preceding one. You cannot have'
                                            ' same waypoints those are adjacent to each other. I.e. A->B->B->C must be either A->B->C or A->B->C->B.')
                                          % waypoint.address_id.name)
                last_waypoint = waypoint

    def subscribe_drivers(self):
        """ Add driver and assistants to the trip followers. """
        for r in self:
            subscribers = []
            if r.driver_id:
                subscribers += [r.driver_id.id]
            if r.assistant_ids:
                subscribers += r.assistant_ids.ids
            if subscribers:
                r.message_subscribe(subscribers)

    def action_confirm(self):
        for r in self:
            r.check_operation_overlap()
            if not r.trip_waypoint_ids:
                raise ValidationError(_("You cannot confirm a trip which has no waypoint. Please add one before you can confirm the trip."))
            r.write({'state': 'confirmed'})
        self.subscribe_drivers()

    def action_cancel(self):
        for r in self:
            if r.state in ('done', 'progress') and not self.env.user.has_group('to_fleet_operation_planning.fleet_group_operator'):
                raise ValidationError(_('Only users with Operator access rights can cancel a trip that is in either In Operation or Done state!'))
            r.write({'state': 'cancelled', 'operation_start': False, 'operation_end': False, 'odometer_ids': [(2, o.id) for o in r.odometer_ids]})

    def action_draft(self):
        for r in self:
            if r.state in ('progress', 'done'):
                raise UserError(_('You cannot set-to-draft a trip that is in either In Operation or Done state!'))
            r.write({'state': 'draft', 'operation_start': False, 'operation_end': False})

    def _prepare_route_waypoint_data(self, address):
        return {
            'address_id':address.id,
            'stop_duration': 0.0
            }

    @api.model
    def _prepare_new_route_data(self, address_ids):
        waypoint_ids = []
        route_section_line_ids = []

        last = False
        sequence = 1

        Route = self.env['route.route']
        for address in address_ids:
            waypoint_ids.append((0, 0, self._prepare_route_waypoint_data(address)))

            if last:
                line = Route._prepare_route_section_line_data(last, address, sequence)
                section = self.trip_section_ids.filtered(lambda r: r.address_from_id == last and r.address_to_id == address)
                if section:
                    line.update({
                        'distance': section.distance,
                        'ave_speed': section.ave_speed,
                        })
                route_section_line_ids.append((0, 0, line))
            sequence += 1
            last = address

        return {
            'name': ' -> '.join(address_ids.mapped('name')),
            'waypoint_ids': waypoint_ids,
            'route_section_line_ids': route_section_line_ids,
            }

    @api.model
    def create_route_if_not_exist(self, raise_error_if_dupplication_found=False):
        address_ids = self.trip_waypoint_ids.mapped('address_id')
        route_id = False
        Route = self.env['route.route']
        route_ids = Route.search([('address_ids', 'child_of', address_ids.ids)])

        if route_ids:
            route_ids = route_ids.filtered(lambda route: route.waypoint_ids.mapped('address_id') == address_ids)
            if route_ids:
                route_id = route_ids[0]

            # raise error if dupplication found
            if len(route_ids) > 1 and raise_error_if_dupplication_found:
                debug_info = ""
                for item in route_ids:
                    debug_info += _("- Route Name: %s; Route ID: %s\n") % (item.name, item.id)

                raise ValidationError(_("We found same routes in your data. Here is the information for your debugging:\n"
                                        "%s\n"
                                        "You must delete %s of those routes"
                                        " before you can proceeding further") % (debug_info, len(route_ids) - 1))

        if not route_id:
            route_id = Route.create(self._prepare_new_route_data(address_ids))
        return route_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('fleet.vehicle.trip') or '/'
        records = super(FleetVehicleTrip, self).create(vals_list)
        for record in records:
            if record.operator_id:
                record.message_subscribe([record.operator_id.partner_id.id])
            if record.trip_waypoint_ids:
                route_id = record.create_route_if_not_exist()
                if route_id.id != record.route_id.id:
                    record.route_id = route_id
        return records

    def write(self, vals):
        if 'operator_id' in vals.keys():
            ResUsers = self.env['res.users']
            operator_id = ResUsers.browse(vals['operator_id'])
            for r in self:
                if r.operator_id:
                    if r.operator_id.partner_id.id in r.message_follower_ids.partner_id.ids:
                        r.message_unsubscribe([r.operator_id.partner_id.id])

                if operator_id:
                    r.message_subscribe([operator_id.partner_id.id])

        res = super(FleetVehicleTrip, self).write(vals)

        if 'trip_waypoint_ids' in vals:
            for trip_id in self.filtered(lambda t: t.trip_waypoint_ids):
                route_id = trip_id.create_route_if_not_exist()
                if route_id.id != trip_id.route_id.id:
                    trip_id.route_id = route_id
        return res

    def unlink(self):
        for r in self:
            if r.state != 'draft':
                raise UserError(("You can only delete records whose state is draft."))
        return super(FleetVehicleTrip, self).unlink()

    def action_trip_report_send(self):
        '''
        This function opens a window to compose an email, with the trip template message loaded by default
        '''
        self.ensure_one()

        try:
            template_id = self.env.ref('to_fleet_operation_planning.email_template_trip_schedule')
        except ValueError:
            template_id = False

        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form')
        except ValueError:
            compose_form_id = False

        ctx = dict()
        ctx.update({
            'default_model': 'fleet.vehicle.trip',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'custom_layout': "to_fleet_operation_planning.mail_template_data_notification_email_fleet_vehicle_trip"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id.id, 'form')],
            'view_id': compose_form_id.id,
            'target': 'new',
            'context': ctx,
        }

