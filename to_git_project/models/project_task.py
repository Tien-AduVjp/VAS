from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _get_default_git_repo(self):
        return self.project_id and self.project_id.git_repository_id or False

    git_repository_id = fields.Many2one('git.repository', string='Git Repo.', help="Git Repostory to which this task concerns",
                                        tracking=True, default=_get_default_git_repo)
    git_branch_id = fields.Many2one('git.branch', string='Git Branch', help="Git Branch to which this task concerns",
                                    domain="[('repository_id', '=', git_repository_id)]",
                                    tracking=True)

    @api.onchange('project_id')
    def _onchange_project_id_load_git(self):
        self.git_repository_id = self._get_default_git_repo()

    @api.constrains('git_repository_id', 'git_branch_id')
    def _check_constrains_git_repository_id_git_branch_id(self):
        for r in self:
            if not r.git_repository_id:
                if r.git_branch_id:
                    raise ValidationError(_('You cannot input a branch without its repository!'))

            elif r.git_branch_id:
                if r.git_branch_id.repository_id.id != r.git_repository_id.id:
                    raise ValidationError(_('You cannot select a branch that does not belong to the repository %s')
                                          % (r.git_repository_id.name,))

    @api.onchange('git_repository_id')
    def _onchange_git_repository_id(self):
        if self.git_repository_id:
            self.git_branch_id = self.git_repository_id.get_default_branch()
        else:
            self.git_branch_id = False
