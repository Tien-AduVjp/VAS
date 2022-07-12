from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResStateGroups(models.Model):
    _name = 'res.state.group'
    _description = 'Country State Group'

    name = fields.Char(string='State Group Name', required=True, translate=True)
    code = fields.Char('State Group Code')
    parent_id = fields.Many2one('res.state.group', string='Parent', help="The parent state group to which the current group belongs.")
    child_ids = fields.One2many('res.state.group', 'parent_id', string='Sub State Group', help="The state groups that belong to the current group")
    country_id = fields.Many2one('res.country', string='Country', required=True,
                                 help="The country to which this state group belong")
    country_state_ids = fields.One2many(string='Country State', related='country_id.state_ids', help="Technical field to support domain country states")
    state_ids = fields.One2many('res.country.state', 'state_group_id', string='States', required=True,
                                domain="[('id', 'in', country_state_ids)]",
                                help="States/Provinces in this group")

    _sql_constraints = [
        ('name_country_unique',
         'UNIQUE(name,country_id)',
         "The name of must be unique per country!"),
        ('code_country_unique',
         'UNIQUE(code,country_id)',
         "The code of a state group must be unique per country!"),
    ]

    @api.constrains('parent_id', 'country_id')
    def _check_parent(self):
        for r in self:
            if r.parent_id and r.parent_id.country_id != r.country_id:
                raise ValidationError(_("It seems that you have wrong parent state group while the parent"
                                        " state group is in a different country."))
            if r.parent_id and r.parent_id.parent_id == r:
                raise ValidationError(_("%s is child of %s already, you can not have reverse relationship.")
                                      % (r.parent_id.name, r.name))

    @api.constrains('state_ids')
    def _check_state_ids(self):
        for r in self:
            if len(r.state_ids.mapped('country_id')) > 1:
                raise ValidationError(_("All the states of the same state group must has the same country"))

    @api.constrains('state_ids', 'country_id')
    def _check_states_country(self):
        for r in self:
            for state_id in r.state_ids:
                if state_id.country_id != r.country_id:
                    raise ValidationError(_("The state %s does not belong to the country %s. It belongs to %s.")
                                          % (state_id.name, r.country_id.name, state_id.country_id.name))

    @api.onchange('parent_id')
    def _onchange_parent(self):
        if self.parent_id:
            self.country_id = self.parent_id.country_id
