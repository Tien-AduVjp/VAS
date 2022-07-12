from odoo import api, fields, models, _


class OkrNode(models.Model):
    _inherit = 'okr.node'

    project_task_ids = fields.One2many('project.task', 'okr_node_id', string="Project Tasks")
    project_ids = fields.Many2many('project.project', 'okr_node_project_rel', 'node_id', 'project_id', string='Projects',
                                   compute='_compute_projects', store=True)
    project_tasks_count = fields.Integer('Project Tasks Count', compute='_compute_project_tasks_count')
    projects_count = fields.Integer('Projects Count', compute='_compute_projects_count')

    @api.depends('project_task_ids.project_id')
    def _compute_projects(self):
        for r in self:
            r.project_ids = [(6, 0, r.project_task_ids.mapped('project_id').ids)]

    def _compute_project_tasks_count(self):
        total_task_data = self.env['project.task'].read_group([('okr_node_id', 'in', self.ids)], ['okr_node_id'], ['okr_node_id'])
        mapped_data = dict([(dict_data['okr_node_id'][0], dict_data['okr_node_id_count']) for dict_data in total_task_data])
        for r in self:
            r.project_tasks_count = mapped_data.get(r.id, 0)

    def _compute_projects_count(self):
        for r in self:
            r.projects_count = len(r.project_ids)

    def action_view_project_tasks(self):
        self.ensure_one()
        project_tasks = self.mapped('project_task_ids')
        result = self.env['ir.actions.act_window']._for_xml_id('project.action_view_task')
        result["domain"] = [('okr_node_id', '=', self.id)]
        result["context"] = {
            'default_okr_node_id': self.id,
            }
        if self.project_ids and len(self.project_ids) == 1:
            result["context"]['default_project_id'] = self.project_ids[0].id
        result['views'] = [(False, 'tree'), (False, 'form')]
        project_tasks_count = len(project_tasks)
        if project_tasks_count == 1:
            res = self.env.ref('project.view_task_form2', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.project_task_ids.id
        return result

    def action_view_projects(self):
        self.ensure_one()
        projects = self.mapped('project_ids')
        action = self.env['ir.actions.act_window']._for_xml_id('project.open_view_project_all')
        action["domain"] = [('id', 'in', projects.ids)]
        return action
