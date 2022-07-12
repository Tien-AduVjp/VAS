from odoo import models, fields, api


class WebsiteDocCategory(models.Model):
    _inherit = 'website.doc.category'

    git_repository_id = fields.Many2one('git.repository', string='Git Document Repo', help='The git repository that contains Documentation in Rst. format')
    git_branch_ids = fields.One2many('git.branch', 'website_doc_category_id', string='Git Document Branches', compute='_compute_git_branch_ids', store=True)

    @api.depends('git_repository_id', 'git_repository_id.branch_ids')
    def _compute_git_branch_ids(self):
        for r in self:
            branch_ids = r.git_repository_id.branch_ids.filtered(lambda b:b.odoo_version_id)
            r.update({
                'git_branch_ids':[(6, 0, branch_ids.ids)],
                })

