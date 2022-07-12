from odoo import models, fields


class GitRepository(models.Model):
    _inherit = 'git.repository'

    project_ids = fields.One2many('project.project', 'git_repository_id', string='Projects')
    task_ids = fields.One2many('project.task', 'git_repository_id', string='Tasks')
    tasks_count = fields.Integer(string='Tasks Count', compute='_compute_tasks_count', groups="project.group_project_user")
    projects_count = fields.Integer(string='Projects Count', compute='_compute_projects_count', groups="project.group_project_user")

    def _compute_tasks_count(self):
        total_data = self.env['project.task'].read_group([('git_repository_id', 'in', self.ids)], ['git_repository_id'], ['git_repository_id'])
        mapped_data = dict([(dict_data['git_repository_id'][0], dict_data['git_repository_id_count']) for dict_data in total_data])
        for r in self:
            r.tasks_count = mapped_data.get(r.id, 0)

    def _compute_projects_count(self):
        total_data = self.env['project.project'].read_group([('git_repository_id', 'in', self.ids)], ['git_repository_id'], ['git_repository_id'])
        mapped_data = dict([(dict_data['git_repository_id'][0], dict_data['git_repository_id_count']) for dict_data in total_data])
        for r in self:
            r.projects_count = mapped_data.get(r.id, 0)

    def action_view_tasks(self):
        action = self.env['ir.actions.act_window']._for_xml_id('project.act_project_project_2_project_task_all')

        # reset context
        action['context'] = {}
        if len(self) == 1:
            action['context'].update({
                'default_git_repository_id': self.id,
                })

        # choose the view_mode accordingly
        tasks = self.mapped('task_ids')
        tasks_count = len(tasks)
        if tasks_count != 1:
            action['domain'] = "[('git_repository_id', 'in', %s)]" % str(self.ids)
        elif tasks_count == 1:
            res = self.env.ref('project.view_task_form2', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = tasks.id
        return action

    def action_view_projects(self):
        action = self.env['ir.actions.act_window']._for_xml_id('project.open_view_project_all')

        # reset context
        action['context'] = {}
        if len(self) == 1:
            action['context'].update({
                'default_git_repository_id': self.id
                })

        # choose the view_mode accordingly
        projects = self.mapped('project_ids')
        projects_count = len(projects)
        if projects_count != 1:
            action['domain'] = "[('git_repository_id', 'in', %s)]" % str(self.ids)
        elif projects_count == 1:
            res = self.env.ref('project.edit_project', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = projects.id
        return action
