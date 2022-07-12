from odoo import models, fields, api


class OdooModuleVersion(models.Model):
    _inherit = 'odoo.module.version'

    task_ids = fields.One2many('project.task', 'odoo_module_version_id', string='Tasks', help="The tasks related to this module version")
    tasks_count = fields.Integer(string='Tasks Count', compute='_compute_tasks_count')
    project_ids = fields.Many2many('project.project', 'odoo_module_version_project_rel', 'odoo_module_version_id', 'project_id', string='Projects',
                                   compute='_compute_projects', store=True)
    projects_count = fields.Integer(string='Projects Count', compute='_compute_projects_count')

    def _compute_tasks_count(self):
        for r in self:
            r.tasks_count = len(r.task_ids)

    def _compute_projects_count(self):
        for r in self:
            r.projects_count = len(r.project_ids)

    @api.depends('task_ids', 'task_ids.project_id')
    def _compute_projects(self):
        for r in self:
            r.project_ids = r.task_ids.mapped('project_id')

    def action_view_tasks(self):
        self.ensure_one()
        action = self.env.ref('project.action_view_task')
        list_view_id = self.env.ref('project.view_task_tree2').id
        form_view_id = self.env.ref('project.view_task_form2').id

        # prepare context
        ctx = {
            'group_by': 'stage_id',
            'default_odoo_module_version_ids': [(4, self.id)],
            'default_git_repository_id': self.git_repository_id.id,
            'default_git_branch_id': self.git_branch_id.id,
            }
        if self.project_ids:
            ctx.update({
                'default_project_id': self.project_ids[0].id
                })

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[False, 'kanban'], [list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot'], [False, 'graph']],
            'target': action.target,
            'context': str(ctx),
            'res_model': action.res_model,
        }
        tasks_count = self.tasks_count
        if tasks_count > 1:
            result['domain'] = "[('id','in',%s)]" % self.task_ids.ids
        elif tasks_count == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = self.task_ids.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
