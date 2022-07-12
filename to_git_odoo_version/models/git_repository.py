from odoo import models, fields, api


class GitRepository(models.Model):
    _inherit = 'git.repository'

    is_odoo_source_code = fields.Boolean(string='Is Odoo Source Code', compute='_compute_is_odoo_source_code', store=True,
                                         help="This field indicates if the repository contains a branch that stores Odoo's source code base, which is also known as Odoo CE.\n"
                                           "Note: The value of this field will be updated automatically when the branch will be updated from remote git.")
    is_odoo_enterprise_source_code = fields.Boolean(string='Is Odoo Enterprise Repo', help="This field indicates if this repository is the Odoo Enterprise source base"
                                                    " that contains Enterprise Modules built on top of Odoo CE")
    default_license_version_id = fields.Many2one('product.license.version', string='Default License Version', help="Unless otherwise specified"
                                                 " (e.g. in the module's manifest), all the source code of this repository will be considered as"
                                                 " being released under this license.")

    @api.depends('branch_ids')
    def _compute_is_odoo_source_code(self):
        for r in self:
            is_odoo_source_code = False
            for branch_id in r.branch_ids:
                if branch_id.is_odoo_source_code:
                    is_odoo_source_code = True
                    break
            r.is_odoo_source_code = is_odoo_source_code

    def action_assign_odoo_versions(self):
        branches = self.mapped('branch_ids')
        branches._assign_odoo_version()

