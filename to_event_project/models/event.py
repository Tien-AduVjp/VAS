from odoo import fields, models, api, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    project_ids = fields.One2many('project.project', 'event_id', string="Projects", groups='project.group_project_user')
    project_count = fields.Integer(compute='_compute_project_count', string="Projects Count", store=True,
                                   help='Total number of projects linked to this event')

    @api.depends('project_ids')
    def _compute_project_count(self):
        project_data = self.env['project.project'].read_group([('event_id', 'in', self.ids)], ['event_id'], ['event_id'])
        result = dict((data['event_id'][0], data['event_id_count']) for data in project_data)
        for r in self:
            r.project_count = result.get(r.id, 0)

    def action_view_projects(self):
        self.ensure_one()
        action = self.env.ref('project.open_view_project_all')
        result = action.read()[0]
        result['context'] = {
            'default_event_id': self.id,
            'default_company_id': self.company_id.id
            }
        result['domain'] = [('event_id', '=', self.id)]
        return result

    def get_project_view_form_simplified(self):
        context = self._context.copy()
        context['default_event_id'] = self.id
        return {
            'name': _("Create Project"),
            'res_model': "project.project",
            'type': "ir.actions.act_window",
            'context': context,
            'view_mode': "form",
            'view_type': "form",
            'view_id': self.env.ref("project.project_project_view_form_simplified_footer").id,
            'target': "new"
        }
