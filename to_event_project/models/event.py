from odoo import fields, models, api, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    project_ids = fields.One2many('project.project', 'event_id', string='Projects', groups='project.group_project_user')
    project_count = fields.Integer(compute='_compute_project_count', string='Projects Count', store=True,
                                   help='Total number of projects linked to this event')

    @api.depends('project_ids')
    def _compute_project_count(self):
        project_data = self.env['project.project'].read_group([('event_id', 'in', self.ids)], ['event_id'], ['event_id'])
        result = dict((data['event_id'][0], data['event_id_count']) for data in project_data)
        for r in self:
            r.project_count = result.get(r.id, 0)

    def action_view_projects(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('project.open_view_project_all')
        action['context'] = {
            'default_event_id': self.id,
            'default_company_id': self.company_id.id
            }
        action['domain'] = [('event_id', '=', self.id)]
        return action
