from odoo import fields, models, api, _
from odoo.exceptions import UserError


class RouteSection(models.Model):
    _name = 'route.section'
    _inherit = 'mail.thread'
    _description = 'Route Section'

    name = fields.Char(string="Section Name", compute='_get_name', store=True, readonly=True)
    address_from_id = fields.Many2one('res.partner', string="From", required=True, index=True, tracking=True)
    address_to_id = fields.Many2one('res.partner', string="To", required=True, index=True, tracking=True)
    distance = fields.Float(string='Distance (km)', help='The distance in kilometers between the From and To', required=True, default=0.0)
    distance_in_miles = fields.Float(string='Distance (mi.)', help='The distance in miles between the From and To', compute='_compute_distance_in_miles', store=True)
    ave_speed = fields.Float(string='Max. Speed', help='The maximum speed in kilometer/hour that you can reach on this section', required=True, default=0.0)
    est_trip_time = fields.Float(string='Est. Time',
                                 compute='_compute_est_trip_time', store=True,
                                 help='The estimated time in hours spent to go through the section')
    route_section_line_ids = fields.One2many('route.section.line', 'section_id', string='Route Section Line')

    _sql_constraints = [
        ('address_from_id_address_to_id_unique',
         'UNIQUE(address_from_id, address_to_id)',
         "Section must be unique!"),
    ]

    @api.depends('distance')
    def _compute_distance_in_miles(self):
        km2mile = self.env['to.base'].km2mile
        for r in self:
            r.distance_in_miles = km2mile(r.distance)

    @api.depends('address_from_id', 'address_to_id', 'address_from_id.name', 'address_to_id.name')
    def _get_name(self):
        for r in self:
            if r.address_from_id and r.address_to_id:
                r.name = r.address_from_id.name + ' - ' + r.address_to_id.name

    @api.depends('distance', 'ave_speed')
    def _compute_est_trip_time(self):
        for r in self:
            r.est_trip_time = r.ave_speed > 0 and r.distance / r.ave_speed or 0.0

    @api.constrains('distance')
    def distance_negative_check(self):
        if self.distance < 0.0:
            raise UserError(_('The distance must not be negative!'))

    @api.constrains('ave_speed')
    def ave_speed_negative_check(self):
        if self.ave_speed < 0.0:
            raise UserError(_('The max speed must not be negative!'))
