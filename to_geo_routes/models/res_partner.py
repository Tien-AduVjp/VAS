from odoo import fields, models, api, _
from odoo.exceptions import UserError

class Partner(models.Model):
    _inherit = 'res.partner'

    waypoint_area_id = fields.Many2one('route.waypoint.area', ondelete='restrict', string='Waypoint Area', help='This field is to group partner addresses into an area')
    route_waypoint_ids = fields.One2many('route.waypoint', 'address_id', string='Waypoints', help="The Waypoints on routes that base on this address")
    route_ids = fields.Many2many('route.route', help="Routes that go through this address")
    routes_count = fields.Integer(string='Routes Count', compute='_compute_routes_count', store=True)

    @api.depends('route_ids')
    def _compute_routes_count(self):
        for r in self:
            r.routes_count = len(r.route_ids)

    @api.constrains('waypoint_area_id', 'state_id', 'country_id')
    def _check_waypoint_area_id(self):
        for r in self:
            if r.waypoint_area_id:
                waypoint_area_partners = self.search([('waypoint_area_id', '=', r.waypoint_area_id.id)])

                if r.waypoint_area_id.restricted_by == 'state' and r.state_id:
                    states = [partner.state_id for partner in waypoint_area_partners]
                    states.append(r.state_id)
                    if len(set(states)) > 1:
                        raise UserError(_('The current waypoint area "%s" does not allow partners having state other than "%s"') % (r.waypoint_area_id.name, states[0].name))
                elif r.waypoint_area_id.restricted_by == 'country' and r.country_id:
                    countries = [partner.country_id for partner in waypoint_area_partners]
                    countries.append(r.country_id)
                    if len(set(countries)) > 1:
                        raise UserError(_('The current waypoint area "%s" does not allow partners having country other than "%s"') % (r.waypoint_area_id.name, countries[0].name))
