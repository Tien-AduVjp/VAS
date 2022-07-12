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
        action = self.env['ir.actions.act_window']._for_xml_id('project.action_view_task')

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
        action['context'] = ctx
        tasks_count = self.tasks_count
        if tasks_count > 1:
            action['domain'] = "[('id','in',%s)]" % self.task_ids.ids
        elif tasks_count == 1:
            action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
            action['res_id'] = self.task_ids.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
