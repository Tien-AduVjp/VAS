from odoo import models


class Project(models.Model):
    _inherit = 'project.project'

    def unlink(self):
        if self.env.user.has_group('project.group_project_user') and not self.env['account.analytic.line'].check_access_rights('read', False):
            self = self.sudo()
        return super(Project, self).unlink()

    def _create_analytic_account_from_values(self, values):
        if self.env.user.has_group('project.group_project_user') and not self.env['account.analytic.account'].check_access_rights('create', False):
            return super(Project, self.sudo())._create_analytic_account_from_values(values)
        else:
            return super(Project, self)._create_analytic_account_from_values(values)
