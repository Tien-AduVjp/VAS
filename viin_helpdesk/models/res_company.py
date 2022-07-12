from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    default_helpdesk_team_id = fields.Many2one('helpdesk.team', string='Default Helpdesk Team',
                                               help="The default helpdesk team that will be assigned to the "
                                               "helpdesk ticket of this company once none is given.")


    @api.model_create_multi
    def create(self, vals_list):
        companies = super(Company, self).create(vals_list)
        companies._create_helpdesk_team_if_not_exits()
        return companies

    def _create_helpdesk_team_if_not_exits(self):
        Team = self.env['helpdesk.team'].sudo()
        team_name = 'General'
        for r in self:
            team = Team.with_context(lang='en_US').search([
                ('name', '=', team_name),
                ('company_id', '=', r.id)
            ], limit=1)
            if not team:
                team = Team.create({
                    'name': team_name,
                    'team_leader_id': self.env.ref('base.user_admin').id,
                    'company_id': r.id
                    })
                r.default_helpdesk_team_id = team.id
