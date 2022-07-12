from odoo import models, fields, api


class GitRepository(models.Model):
    _inherit = 'git.repository'

    odoo_module_version_ids = fields.One2many('odoo.module.version', 'git_repository_id', string='Odoo Module Versions', readonly=True)
    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions_count')
    odoo_module_ids = fields.Many2many('odoo.module', 'git_repo_odoo_module_rel', 'git_repository_id', 'odoo_module_id', string='Odoo Modules',
                                       compute='_compute_odoo_modules', store=True)
    odoo_modules_count = fields.Integer(string='Odoo Modules Count', compute='_compute_odoo_modules_count')
    exclude_dependencies_from_repo_ids = fields.Many2many('git.repository', 'exclude_dependencies_git_repo_rel', 'repo_id', 'excl_repo_id',
                                                          string='Exclude Dependencies From', help="When generating dependencies"
                                                        " for the Odoo modules in the current repository, the Odoo modules from the excluded"
                                                        " repositories specified here will be excluded also.")
    app_product_templates_count = fields.Integer(string='App Product Templates Count', compute='_compute_app_product_templates_count')

    @api.depends('odoo_module_version_ids.product_id.product_tmpl_id')
    def _compute_app_product_templates_count(self):
        for r in self:
            r.app_product_templates_count = len(r.odoo_module_version_ids.mapped('product_id.product_tmpl_id'))

    @api.depends('odoo_module_version_ids', 'odoo_module_version_ids.module_id')
    def _compute_odoo_modules(self):
        for r in self:
            r.odoo_module_ids = [(6, 0, r.odoo_module_version_ids.mapped('module_id').ids)]

    def _compute_odoo_module_versions_count(self):
        # Use sudo to allow users access the repository form view without acquiring the group Odoo Apps Management/User
        odoo_module_versions_data = self.env['odoo.module.version'].sudo().read_group([('git_repository_id', 'in', self.ids)], ['git_repository_id'], ['git_repository_id'])
        mapped_data = dict([(dict_data['git_repository_id'][0], dict_data['git_repository_id_count']) for dict_data in odoo_module_versions_data])
        for r in self:
            r.odoo_module_versions_count = mapped_data.get(r.id, 0)

    def _compute_odoo_modules_count(self):
        # Use sudo to allow users access the repository form view without acquiring the group Odoo Apps Management/User
        for r in self.sudo():
            r.odoo_modules_count = len(r.odoo_module_ids)

    def scan_for_branches_and_checkout(self):
        self.scan_for_branches()
        # TODO(@namkazt): later we can set _depth from a config field when checkout branch
        # set _depth = 0 to fetch complete branch, _depth > 0 to fetch number of commits from HEAD
        self.mapped('branch_ids').checkout(_depth=0)

    def action_view_odoo_module_versions(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        action = self.env.ref('to_odoo_module.odoo_module_version_action')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        # choose the view_mode accordingly
        modules_count = len(odoo_module_versions)
        if modules_count != 1:
            result['domain'] = "[('git_repository_id', 'in', %s)]" % str(self.ids)
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_versions.id
        return result

    def action_view_odoo_modules(self):
        odoo_modules = self.mapped('odoo_module_ids')
        action = self.env.ref('to_odoo_module.odoo_module_action')
        result = action.read()[0]

        # choose the view_mode accordingly
        modules_count = len(odoo_modules)
        if modules_count != 1:
            result['domain'] = "[('git_repository_ids', 'in', %s)]" % str(self.ids)
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_modules.id
        return result

    def action_view_app_product_templates(self):
        product_templates = self.mapped('odoo_module_version_ids.product_id.product_tmpl_id')
        action = self.env.ref('product.product_template_action')
        result = action.read()[0]
        # get rid off default context and domain
        result['context'] = {}

        # choose the view_mode accordingly
        product_tmpl_count = len(product_templates)
        if product_tmpl_count != 1:
            result['domain'] = [('is_odoo_app', '=', True), ('id', 'in', product_templates.ids)]
        elif product_tmpl_count == 1:
            res = self.env.ref('product.product_template_only_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = product_templates.id
        return result

