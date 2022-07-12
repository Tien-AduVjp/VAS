from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    ticket_ids = fields.One2many('helpdesk.ticket', 'project_id', string='Helpdesk Tickets')
    tickets_count = fields.Integer(string='Tickets', compute='_compute_tickets_count')
    helpdesk_team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team',
                                       help="The Helpdesk Team used by default for ticket that is created from this project.")

    def _compute_tickets_count(self):
        projects_data = self.env['helpdesk.ticket'].read_group([('project_id', 'in', self.ids)], ['project_id'], ['project_id'])
        mapped_data = dict([(dict_data['project_id'][0], dict_data['project_id_count']) for dict_data in projects_data])
        for r in self:
            r.tickets_count = mapped_data.get(r.id, 0)

    def action_tickets_view(self):
        self.ensure_one()
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_project_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_team_id': self.helpdesk_team_id.id or self.env.company.default_helpdesk_team_id.id
            })

        return {
            'name': 'Tickets',
            'view_mode': 'kanban,tree,form,pivot,calendar,graph',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('id', 'in', self.ticket_ids.ids)],
        }

    def name_get(self):
        if self._context.get('allow_timesheet', False):
            return super(Project, self.sudo()).name_get()
        return super(Project, self).name_get()
