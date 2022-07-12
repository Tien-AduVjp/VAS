from odoo import api, fields, models, _


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    
    driver_done_trip_ids = fields.One2many('fleet.vehicle.trip', 'employee_id', string='Trips',
                                    domain=[('state', '=', 'done')],
                                    help='Total trips that employee takes as the role of driver')
    driver_done_trips_count = fields.Integer(string='Trips Count', compute='_count_driver_done_trips', compute_sudo=True, groups='hr.group_hr_user')

    assitant_done_trip_ids = fields.Many2many('fleet.vehicle.trip', string='Trips Done (as Assistant)',
                                    compute='_compute_assitant_done_trip_ids', store=True,
                                    groups='hr.group_hr_user',
                                    help='Total trips that employee takes as the role of driver')
    assitant_done_trips_count = fields.Integer(string='Trips Done (as Assistant) Count', compute='_count_assitant_done_trips', compute_sudo=True, groups='hr.group_hr_user')

    @api.depends('driver_done_trip_ids')
    def _count_driver_done_trips(self):
        # TODO: master/14+ rename this to `_compute_assitant_done_trips_count` for convention
        vals_list = self.env['fleet.vehicle.trip'].read_group(
            [('employee_id', 'in', self.ids), ('state', '=', 'done')],
            ['employee_id'],
            ['employee_id']
            )
        mapped_data = dict([(vals['employee_id'][0], vals['employee_id_count']) for vals in vals_list])
        for r in self:
            r.driver_done_trips_count = mapped_data.get(r.id, 0)

    @api.depends('address_home_id', 'user_id.partner_id')
    def _compute_assitant_done_trip_ids(self):
        for r in self:
            r.assitant_done_trip_ids = (r.user_id.partner_id | r.address_home_id).assistant_done_trip_ids

    @api.depends('assitant_done_trip_ids')
    def _count_assitant_done_trips(self):
        for r in self:
            r.assitant_done_trips_count = len(r.assitant_done_trip_ids) or 0

