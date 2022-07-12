from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    git_repository_id = fields.Many2one('git.repository', string='Default Git Repo.',
                                        help="The default Git Repostory of the project which will be filled automatically when handling tasks and issues",
                                        tracking=True)


