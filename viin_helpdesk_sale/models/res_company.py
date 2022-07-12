from odoo import models


class Company(models.Model):
    _inherit = "res.company"

    def _create_helpdesk_team_if_not_exits(self):
        super(Company, self)._create_helpdesk_team_if_not_exits()
        
        Team = self.env['helpdesk.team'].sudo()
        team_name = 'Customer Support'
        vals_list = []
        for r in self:
            team = Team.with_context(lang='en_US').search([
                ('name', '=', team_name),
                ('company_id', '=', r.id)
            ], limit=1)
            if not team:
                vals_list.append({
                    'name': team_name,
                    'team_leader_id': self.env.ref('base.user_admin').id,
                    'company_id': r.id,
                    })
        
        if vals_list:
            Team.create(vals_list)
