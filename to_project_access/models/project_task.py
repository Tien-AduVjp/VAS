from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    allowed_user_ids = fields.Many2many(groups='project.group_project_user')

    def write(self, vals):
        """
        This override make sure internal users who have read access to a project task can always change its kanban state
        """
        if 'kanban_state' in vals and len(vals) == 1 and self.env.user.has_group('base.group_user') and self.check_access_rights('read'):
            self.check_access_rule('read')
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except Exception:
                return super(ProjectTask, self.sudo()).write(vals)
        return super(ProjectTask, self).write(vals)

    def unlink(self):
        self.check_access_rule('unlink')
        if self.env.user.has_group('project.group_project_user') and (not self.env['account.analytic.line'].check_access_rights('read', False)
                or not self.env.user.has_group('analytic.group_analytic_accounting')):
            return super(ProjectTask, self.sudo()).unlink()
        return super(ProjectTask, self).unlink()
