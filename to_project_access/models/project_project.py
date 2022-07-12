from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    def _default_project_user_full_access_rights(self):
        if self.env.user.has_group('project.group_project_user') and not self.env.user.has_group('project.group_project_manager'):
            return True
        return self.env.company.project_user_full_access_rights

    project_user_full_access_rights = fields.Boolean(string='Grant Full Access Rights',
                                                     default=_default_project_user_full_access_rights,
                                                     groups='project.group_project_manager',
                                                     help="If enabled, the manager of the project who belongs to the Project / User "
                                                     "access group will have full rights to this project without adding she or he "
                                                     "to the Project / Administrator group.")

    def unlink(self):
        self.check_access_rule('unlink')
        if self.env.user.has_group('project.group_project_user') and (not self.env['account.analytic.line'].check_access_rights('read', False)
                or not self.env.user.has_group('analytic.group_analytic_accounting')):
            return super(Project, self.sudo()).unlink()
        return super(Project, self).unlink()

    def _create_analytic_account_from_values(self, values):
        if self.env.user.has_group('project.group_project_user') and not self.env['account.analytic.account'].check_access_rights('create', False):
            return super(Project, self.sudo())._create_analytic_account_from_values(values)
        else:
            return super(Project, self)._create_analytic_account_from_values(values)
