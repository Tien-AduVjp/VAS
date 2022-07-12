from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    state_group_id = fields.Many2one('res.state.group', string='State Group')

    @api.constrains('state_group_id', 'country_id')
    def _check_state_group_vs_country(self):
        for r in self:
            if r.state_group_id:
                if r.state_group_id.country_id != r.country_id:
                    raise ValidationError(_("The state %s could not belong to the State Group %s while they have no same country")
                                      % (r.name, r.state_group_id.name))
