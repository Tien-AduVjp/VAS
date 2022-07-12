from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WaypointArea (models.Model):
    _name = 'route.waypoint.area'
    _description = "Waypoint Area"

    name = fields.Char(string='Waypoint Area', translate=True)
    restricted_by = fields.Selection([
        ('none', 'Non-Restricted'),
        ('state', 'State'),
        ('country', 'Country')], string='Restricted By', required=True, default='none',
                                     help='Partner Addresses linked to this area will be restricted by either state or country or non.\n'
                                     'For example, when this are is set restricted by state of Hanoi, only partners with addresses outside Hanoi '
                                     'cannot be linked to this area.')
    partner_ids = fields.One2many('res.partner', 'waypoint_area_id', string='Partners', help='The partners that is listed in this area')

    @api.constrains('restricted_by', 'partner_ids')
    def _check_restricted_by(self):
        for r in self:
            if r.restricted_by == 'state':
                if len(set([partner.state_id for partner in r.partner_ids])) > 1:
                    raise UserError(_('The current partners linked to this waypoint area have diffent states.\n'
                                      ' Hence, you can not make this waypoint area to restrict partners by state'))
            elif r.restricted_by == 'country':
                if len(set([partner.country_id for partner in r.partner_ids])) > 1:
                    raise UserError(_('The current partners linked to this waypoint area are in diffent countries.\n'
                                      ' Hence, you can not make this waypoint area to restrict partners by country'))
