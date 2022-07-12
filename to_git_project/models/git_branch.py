from odoo import models, fields


class GitBranch(models.Model):
    _inherit = 'git.branch'

    task_ids = fields.One2many('project.task', 'git_branch_id', string='Tasks', copy=False)
    tasks_count = fields.Integer(string='Tasks Count', compute='_compute_tasks_count', groups="project.group_project_user")
    projects_count = fields.Integer(string='Projects Count', compute='_compute_projects_count', groups="project.group_project_user")

    def _compute_tasks_count(self):
        total_data = self.env['project.task'].read_group([('git_branch_id', 'in', self.ids)], ['git_branch_id'], ['git_branch_id'])
        mapped_data = dict([(dict_data['git_branch_id'][0], dict_data['git_branch_id_count']) for dict_data in total_data])
        for r in self:
            r.tasks_count = mapped_data.get(r.id, 0)

    def _compute_projects_count(self):
        for r in self:
            projects = r.task_ids.mapped('project_id')
            r.projects_count = len(projects)

    def action_view_tasks(self):
        action = self.env.ref('project.action_view_task')
        result = action.read()[0]

        # reset context
        result['context'] = {}
        if len(self) == 1:
            result['context'].update({
                'default_git_branch_id': self.id,
                'default_git_repository_id': self.repository_id.id,
                })

        # choose the view_mode accordingly
        tasks = self.mapped('task_ids')
        tasks_count = len(tasks)
        if tasks_count != 1:
            result['domain'] = "[('git_branch_id', 'in', %s)]" % str(self.ids)
        elif tasks_count == 1:
            res = self.env.ref('project.view_task_form2', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = tasks.id
        return result

    def action_view_projects(self):
        action = self.env.ref('project.open_view_project_all')
        result = action.read()[0]

        # reset context
        result['context'] = {}
        if len(self) == 1:
            result['context'].update({
                'default_git_repository_id': self.repository_id.id,
                })

        projects = self.mapped('task_ids.project_id')
        result['domain'] = "[('id', 'in', %s)]" % str(projects.ids)
        return result
